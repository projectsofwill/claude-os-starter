#!/usr/bin/env python3
"""
Estimate the API-equivalent (pay-as-you-go) dollar cost of Claude Code usage by
parsing the local transcript JSONL files under ~/.claude/projects and pricing the
recorded token usage at current published per-token rates.

Usage:
  python3 cost.py                      # all time, all projects
  python3 cost.py --since 2026-06-12   # from a date (YYYY-MM-DD or YYYYMMDD)
  python3 cost.py --days 7             # last N days
  python3 cost.py --today              # today only
  python3 cost.py --project work-brain # only project dirs whose path contains this
  python3 cost.py --cache-ttl 1h       # price cache writes at the 1-hour rate (default 5m)
  python3 cost.py --by-session         # + exact per-session breakdown (every token counted once)
  python3 cost.py --by-area            # + APPROXIMATE per-sub-project breakdown (file-path heuristic)
  python3 cost.py --blocks             # show usage grouped into 5-hour billing windows

Notes:
  - This is the API/Console pay-as-you-go cost. On a flat Max subscription you pay
    the monthly fee regardless of token volume; this number is what the same usage
    would have been billed if metered per token.
  - Rates below are per-token, from the model pricing reference. Update RATES if
    pricing changes. Cache read = 0.1x input; cache write = 1.25x (5m) / 2x (1h).
  - --by-session is exact: cost is bucketed per sessionId, each token counted once.
  - --by-area is a heuristic: it attributes a turn's cost to a sub-project only by the
    file paths in that same assistant message. Reasoning/text-only turns carry no path
    and land in (unattributed) - typically the majority of cost. The section prints how
    much of total cost it could actually attribute. Do not read it as precise dollars.
"""
import json, glob, os, argparse, math, re, datetime as dt
from collections import defaultdict

# Per-token rates ($/token): (input, output, cache_read, cache_write_5m, cache_write_1h)
RATES = {
    "fable":  (10e-6, 50e-6, 1.0e-6, 12.5e-6, 20e-6),
    "opus":   (5e-6,  25e-6, 0.5e-6, 6.25e-6, 10e-6),
    "sonnet": (3e-6,  15e-6, 0.3e-6, 3.75e-6, 6e-6),
    "haiku":  (1e-6,  5e-6,  0.1e-6, 1.25e-6, 2e-6),
}

def tier(model):
    m = (model or "").lower()
    if "fable" in m or "mythos" in m: return "fable"
    if "opus" in m: return "opus"
    if "sonnet" in m: return "sonnet"
    if "haiku" in m: return "haiku"
    return "opus"  # unrecognized model - priced at opus rate (may over-estimate); update RATES if needed

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--since", help="YYYY-MM-DD or YYYYMMDD")
    p.add_argument("--days", type=int)
    p.add_argument("--today", action="store_true")
    p.add_argument("--project", help="substring filter on the project dir path")
    p.add_argument("--cache-ttl", choices=["5m", "1h"], default="5m")
    p.add_argument("--by-session", action="store_true",
                   help="exact per-session cost breakdown")
    p.add_argument("--by-area", action="store_true",
                   help="approximate per-sub-project cost (file-path heuristic)")
    p.add_argument("--blocks", action="store_true",
                   help="show usage grouped into 5-hour billing windows (replaces model table)")
    p.add_argument("--changelog", nargs="?", const="ops/CHANGES.log", default=None,
                   help="tag each session with matching CHANGES.log task names "
                        "(default path ops/CHANGES.log); implies --by-session")
    return p.parse_args()

def since_date(a):
    if a.today:
        return dt.date.today().isoformat()
    if a.days:
        return (dt.date.today() - dt.timedelta(days=a.days)).isoformat()
    if a.since:
        s = a.since.replace("-", "")
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None  # all time

def usage_cost(u, t, cw5):
    """Dollar cost of one usage block at the given model tier."""
    ri, ro, rr, rw5, rw1 = RATES[t]
    rw = rw5 if cw5 else rw1
    return ((u.get("input_tokens", 0) or 0) * ri
            + (u.get("output_tokens", 0) or 0) * ro
            + (u.get("cache_read_input_tokens", 0) or 0) * rr
            + (u.get("cache_creation_input_tokens", 0) or 0) * rw)

# --- file-path -> sub-project area (heuristic, --by-area only) -------------------
WS_MARKER = "desktop/claude os/"

def area_of_path(p):
    try:
        q = str(p).replace("\\", "/").lower().rstrip("/")
        i = q.find(WS_MARKER)
        if i == -1:
            if "/.claude/" in q:
                return "(.claude config)"
            return "(external)"
        segs = [s for s in q[i + len(WS_MARKER):].split("/") if s and s != ".."]
        if not segs:
            return "(root)"
        if segs[0] == "projects":
            return f"Projects/{segs[1]}" if len(segs) > 1 else "Projects/(root)"
        if len(segs) == 1:
            return "(root)"  # a file sitting directly in the workspace root
        return segs[0]
    except Exception:
        return "(external)"

def paths_in_message(msg):
    c = msg.get("content")
    if not isinstance(c, list):
        return []
    out = []
    for b in c:
        if isinstance(b, dict) and b.get("type") == "tool_use":
            inp = b.get("input")
            if isinstance(inp, dict):
                fp = inp.get("file_path") or inp.get("path") or inp.get("notebook_path")
                if fp:
                    out.append(fp)
    return out

def dominant_area(paths):
    if not paths:
        return "(unattributed)"
    counts = defaultdict(int)
    for p in paths:
        counts[area_of_path(p)] += 1
    # most-touched area; ties broken alphabetically for determinism
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

def _floor_hour(ts):
    return ts.replace(minute=0, second=0, microsecond=0)

def build_blocks(records, block_hours=5):
    """Group (datetime, cost, tok, model) records into rolling 5-hour windows."""
    if not records:
        return []
    block_dur = dt.timedelta(hours=block_hours)
    blocks = []
    blk = None
    for ts, cost, tok, model in sorted(records, key=lambda x: x[0]):
        if blk is None:
            blk = {"start": _floor_hour(ts), "last": ts, "cost": 0.0, "tok": 0, "models": set()}
        else:
            since_start = ts - blk["start"]
            since_last  = ts - blk["last"]
            if since_start > block_dur or since_last > block_dur:
                blocks.append(blk)
                blk = {"start": _floor_hour(ts), "last": ts, "cost": 0.0, "tok": 0, "models": set()}
        blk["cost"] += cost
        blk["tok"]  += tok
        blk["last"]  = ts
        if model:
            blk["models"].add(model)
    if blk:
        blocks.append(blk)
    return blocks

def print_blocks(blocks, block_hours=5):
    now = dt.datetime.now(dt.timezone.utc)
    block_dur = dt.timedelta(hours=block_hours)
    print(f"{'block start (UTC)':<22}{'status':<22}{'tokens':>14}{'cost $':>11}   models")
    print("-" * 93)
    tot_cost = 0.0
    tot_tok  = 0
    for blk in reversed(blocks):
        end = blk["start"] + block_dur
        is_active = now < end and (now - blk["last"]) < block_dur
        if is_active:
            rem = end - now
            rem_h, rem_m = divmod(int(rem.total_seconds() // 60), 60)
            # burn rate: tokens/min from first→last entry (need >1 entry for a meaningful rate)
            elapsed_min = (blk["last"] - blk["start"]).total_seconds() / 60
            burn_str = ""
            if elapsed_min > 1:
                rate = blk["tok"] / elapsed_min
                proj = blk["tok"] + rate * (rem.total_seconds() / 60)
                burn_str = f"  ~{proj/1000:.0f}k tok projected"
            status = f"ACTIVE {rem_h}h {rem_m}m left"
        else:
            el = blk["last"] - blk["start"]
            el_h, el_m = divmod(int(el.total_seconds() // 60), 60)
            status = f"done  {el_h}h {el_m}m"
            burn_str = ""
        model_tiers = "/".join(sorted({tier(m) for m in blk["models"]}))[:18]
        start_str = blk["start"].strftime("%Y-%m-%d %H:%M")
        line = f"{start_str:<22}{status:<22}{blk['tok']:>14,}{blk['cost']:>11.2f}   {model_tiers}"
        print(to_ascii(line))
        if burn_str:
            print(to_ascii(f"  {burn_str}"))
        tot_cost += blk["cost"]
        tot_tok  += blk["tok"]
    print("-" * 93)
    print(f"{'TOTAL':<22}{'':<22}{tot_tok:>14,}{tot_cost:>11.2f}")

def to_ascii(s):
    """Keep stdout ASCII-safe on a cp1252 Windows console (house rule)."""
    repl = {"→": "->", "←": "<-", "—": "-", "–": "-",
            "…": "...", "•": "*", "’": "'", "‘": "'",
            "“": '"', "”": '"', " ": " "}
    for k, v in repl.items():
        s = s.replace(k, v)
    return s.encode("ascii", "ignore").decode("ascii")

def clean_label(s, n=52):
    s = to_ascii(" ".join(str(s).split()))
    return s[:n] + ("..." if len(s) > n else "")

def first_user_text(msg):
    """First human-readable text from a user message, with harness wrappers stripped.
    Returns "" for pure wrapper/noise messages so the caller can try the next one.
    A slash-command (e.g. /usage-cost) is returned verbatim with its leading slash."""
    c = msg.get("content")
    s = ""
    if isinstance(c, str):
        s = c
    elif isinstance(c, list):
        for b in c:
            if isinstance(b, str):
                s = b; break
            if isinstance(b, dict) and b.get("type") == "text":
                s = b.get("text", ""); break
    if not s:
        return ""
    # slash-command invocation -> use the command name
    m = re.search(r"<command-(?:name|message)>\s*/?([\w:-]+)", s)
    if m:
        return "/" + m.group(1)
    # drop noisy harness blocks (tag + inner text), then any stray tags
    for tag in ("ide_opened_file", "local-command-caveat", "command-message",
                "command-name", "command-args", "system-reminder"):
        s = re.sub(rf"<{tag}>.*?</{tag}>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = " ".join(s.split())
    # a skill invocation injects its body as a user message; not a real prompt
    if s.startswith("Base directory for this skill"):
        return ""
    return s

# --- CHANGES.log cross-reference (--changelog only) -----------------------------
# Hub files appear in almost every task's "files:" list, so they can't distinguish
# one task from another; matching ignores them and joins on distinctive files only.
HUB_FILES = {"changes.log", "status.md", "claude.md", "readme.md", "roadmap.md",
             "agents.md", ".gitignore", "memory.md", "backlog.md", "timeline.md"}

def basename_key(p):
    return str(p).replace("\\", "/").rstrip("/").split("/")[-1].lower()

def parse_changelog(path):
    """Return [(date, task, {distinctive basenames})] from a CHANGES.log file."""
    entries = []
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return entries

    def flush(b):
        if b.get("date") and b.get("task"):
            fs = set()
            for f in b.get("files", "").replace(";", ",").split(","):
                f = re.sub(r"\(.*?\)", "", f).strip()  # drop "(new)" / "(deleted)" notes
                k = basename_key(f)
                if k and k not in ("none", "*") and k not in HUB_FILES:
                    fs.add(k)
            entries.append((b["date"][:10], b["task"], fs))

    block = {}
    for line in text.splitlines():
        if line.strip() == "---":
            flush(block); block = {}
            continue
        m = re.match(r"(date|task|files):\s*(.*)", line.strip())
        if m:
            block[m.group(1)] = m.group(2).strip()
    flush(block)
    return entries

def match_tasks(entries, sess_dates, sess_files):
    """Task names whose date is in the session and that share a distinctive file."""
    out = []
    for d, task, fs in entries:
        if d in sess_dates and (fs & sess_files):
            if task not in out:
                out.append(task)
    return out

def main():
    a = parse_args()
    since = since_date(a)
    cw5 = (a.cache_ttl == "5m")
    cl_entries = None
    if a.changelog:
        a.by_session = True  # the cross-reference enriches the per-session view
        cl_entries = parse_changelog(a.changelog)

    files = sorted(glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True))
    if a.project:
        files = [f for f in files if a.project.lower() in f.lower()]

    agg = defaultdict(lambda: [0, 0, 0, 0])  # model -> [in, out, cache_write, cache_read]
    # session id -> aggregated cost/tokens/last-date (only sessions with usage are emitted)
    # files/dates are populated only for --changelog (used to match CHANGES.log tasks)
    sessions = defaultdict(lambda: {"cost": 0.0, "tok": 0, "date": "",
                                    "files": set(), "dates": set()})
    # session id -> label fields, captured from ANY record (titles live on user records)
    meta = defaultdict(lambda: {"title": "", "prompt": "", "prose": "", "cmd": ""})
    areas = defaultdict(lambda: [0.0, 0])  # area -> [cost, tokens]
    grand_cost = 0.0
    raw_records = []  # for --blocks: (datetime, cost, tok, model)

    for f in files:
        base = os.path.basename(f)
        try:
            fh = open(f, encoding="utf-8")
        except Exception:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                try:
                    ts = r.get("timestamp", "") or ""
                    if since and ts[:10] < since:
                        continue

                    # capture session label fields from any record (incl. user records).
                    # prefer the user's first prose ask; fall back to first meaningful command.
                    sid = r.get("sessionId") or f"file:{base}"
                    m = meta[sid]
                    if not m["title"] and r.get("aiTitle"):
                        m["title"] = r.get("aiTitle")
                    if not m["prompt"] and r.get("lastPrompt"):
                        m["prompt"] = r.get("lastPrompt")
                    if (not m["prose"] or not m["cmd"]) and r.get("type") == "user":
                        ft = first_user_text(r.get("message") or {})
                        if ft and ft not in ("/clear", "/compact"):  # session-control noise
                            if not ft.startswith("/") and not m["prose"]:
                                m["prose"] = ft
                            elif ft.startswith("/") and not m["cmd"]:
                                m["cmd"] = ft

                    msg = r.get("message") or {}
                    u = msg.get("usage") or {}
                    if not u:
                        continue
                    model = msg.get("model") or r.get("model") or ""
                    t = tier(model)
                    cost = usage_cost(u, t, cw5)
                    tok = ((u.get("input_tokens", 0) or 0)
                           + (u.get("output_tokens", 0) or 0)
                           + (u.get("cache_creation_input_tokens", 0) or 0)
                           + (u.get("cache_read_input_tokens", 0) or 0))

                    # blocks collection
                    if a.blocks and ts:
                        try:
                            ts_dt = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            raw_records.append((ts_dt, cost, tok, model))
                        except Exception:
                            pass

                    # model table (existing behavior)
                    v = agg[model]
                    v[0] += u.get("input_tokens", 0) or 0
                    v[1] += u.get("output_tokens", 0) or 0
                    v[2] += u.get("cache_creation_input_tokens", 0) or 0
                    v[3] += u.get("cache_read_input_tokens", 0) or 0
                    grand_cost += cost

                    # per-session (exact). sid computed above (synthetic key if missing)
                    s = sessions[sid]
                    s["cost"] += cost
                    s["tok"] += tok
                    d = ts[:10]
                    if d and d > s["date"]:
                        s["date"] = d

                    # per-session file/date footprint for CHANGES.log matching
                    if a.changelog:
                        if d:
                            s["dates"].add(d)
                        for p in paths_in_message(msg):
                            k = basename_key(p)
                            if k and k not in HUB_FILES:
                                s["files"].add(k)

                    # per-area (heuristic)
                    if a.by_area:
                        area = dominant_area(paths_in_message(msg))
                        ar = areas[area]
                        ar[0] += cost
                        ar[1] += tok
                except Exception:
                    # never let one bad record drop the rest of the transcript
                    continue

    if not agg:
        print("No usage found for that window.")
        return

    if a.blocks:
        window = since or "all time"
        print(f"Window: {window} onward   |   5-hour billing blocks"
              + (f"   |   project~={a.project}" if a.project else ""))
        blocks = build_blocks(raw_records)
        if not blocks:
            print("No timestamped records found for blocks view.")
        else:
            print_blocks(blocks)
        return

    window = since or "all time"
    print(f"Window: {window} onward   |   cache-write priced at {a.cache_ttl} rate"
          + (f"   |   project~={a.project}" if a.project else ""))
    print(f"{'model':<26}{'input':>12}{'output':>12}{'cache_wr':>14}{'cache_rd':>14}{'cost $':>11}")
    print("-" * 89)
    tot = [0, 0, 0, 0]
    tot_cost = 0.0
    for model, (i, o, cw, cr) in sorted(agg.items(), key=lambda kv: -(kv[1][1])):
        ri, ro, rr, rw5, rw1 = RATES[tier(model)]
        rw = rw5 if cw5 else rw1
        cost = i * ri + o * ro + cr * rr + cw * rw
        tot_cost += cost
        for k, val in enumerate((i, o, cw, cr)):
            tot[k] += val
        label = (model or "(none)")[:25]
        print(f"{label:<26}{i:>12,}{o:>12,}{cw:>14,}{cr:>14,}{cost:>11.2f}")
    print("-" * 89)
    print(f"{'TOTAL':<26}{tot[0]:>12,}{tot[1]:>12,}{tot[2]:>14,}{tot[3]:>14,}{tot_cost:>11.2f}")
    print()
    print(f"Total tokens (all types): {sum(tot):,}")
    print(f"API-equivalent (pay-as-you-go) cost: ${tot_cost:,.2f}")

    # --- exact per-session breakdown -------------------------------------------
    if a.by_session:
        rows = sorted(sessions.items(), key=lambda kv: -kv[1]["cost"])
        ssum = sum(s["cost"] for _, s in rows)
        print()
        print(f"By session (exact - every token counted once)   |   {len(rows)} sessions")
        if cl_entries is not None:
            if cl_entries:
                print(to_ascii(
                    f"  ~ likely: best-effort CHANGES.log task guess ({len(cl_entries)} "
                    f"entries, {a.changelog}). Shown only when a session maps to <=4 tasks "
                    f"by same-day + shared file; it is a guess and can be wrong/incomplete."))
            else:
                print(to_ascii(f"  ~ likely: no CHANGES.log entries at {a.changelog} (skipping match)"))
        print(f"{'last-active':<12}{'cost $':>10}{'tokens':>16}   session")
        print("-" * 89)
        TOPN = 25
        for sid, s in rows[:TOPN]:
            mm = meta.get(sid, {})
            lbl = clean_label(mm.get("title") or mm.get("prose") or mm.get("prompt")
                              or mm.get("cmd") or "(untitled)")
            print(f"{s['date'] or '?':<12}{s['cost']:>10.2f}{s['tok']:>16,}   {lbl}")
            if cl_entries is not None:
                tasks = match_tasks(cl_entries, s["dates"], s["files"])
                # only tag cleanly-matched sessions; a big multi-task session matches
                # too many CHANGES.log entries to attribute, so leave its prose label alone
                if 1 <= len(tasks) <= 4:
                    print(f"{'':<38}~ likely: {clean_label('; '.join(tasks), 72)}")
        if len(rows) > TOPN:
            rest = [s for _, s in rows[TOPN:]]
            rc = sum(s["cost"] for s in rest)
            rt = sum(s["tok"] for s in rest)
            print(f"{'':<12}{rc:>10.2f}{rt:>16,}   ... {len(rest)} more sessions")
        print("-" * 89)
        print(f"{'TOTAL':<12}{ssum:>10.2f}")
        if not math.isclose(ssum, tot_cost, rel_tol=1e-9, abs_tol=1e-6):
            print(f"  ! reconciliation off: sessions sum ${ssum:,.4f} vs model sum ${tot_cost:,.4f}")

    # --- approximate per-area breakdown ----------------------------------------
    if a.by_area:
        rows = sorted(areas.items(), key=lambda kv: -kv[1][0])
        asum = sum(c for c, _ in areas.values())
        unattr = areas.get("(unattributed)", [0.0, 0])[0]
        attributed = asum - unattr
        print()
        print("By sub-project area (APPROXIMATE - file-path heuristic, see note below)")
        print(f"{'area':<24}{'cost $':>10}{'% total':>9}{'tokens':>16}")
        print("-" * 89)
        for area, (c, tk) in rows:
            pct = (100 * c / asum) if asum else 0
            print(f"{to_ascii(area):<24}{c:>10.2f}{pct:>8.1f}%{tk:>16,}")
        print("-" * 89)
        print(f"{'TOTAL':<24}{asum:>10.2f}")
        cov = (100 * attributed / asum) if asum else 0
        print(f"Attributed to a sub-project: ${attributed:,.2f} of ${asum:,.2f} "
              f"({cov:.1f}%). The rest is (unattributed) - reasoning/text turns with no "
              f"file op in the same message.")
        print("This split is a heuristic, not precise dollars: a turn touching two areas "
              "is charged whole to its dominant one, and most cost carries no file path.")
        if not math.isclose(asum, tot_cost, rel_tol=1e-9, abs_tol=1e-6):
            print(f"  ! reconciliation off: areas sum ${asum:,.4f} vs model sum ${tot_cost:,.4f}")

    print()
    print("On a flat Max subscription you pay the monthly fee regardless "
          "(Max 5x ~$100/mo, Max 20x ~$200/mo, approximate). This figure is what "
          "the same usage would cost metered per token.")

if __name__ == "__main__":
    main()
