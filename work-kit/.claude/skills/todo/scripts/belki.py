#!/usr/bin/env python3
"""Mechanical write layer for the /todo skill (Belki task store).

Every task WRITE goes through this script -- it enforces what SKILL.md promises,
as backstops rather than instructions (Codex gate + /code-review, 2026-07-06):
LF-only, trailing-newline repair, unique ids, dedupe-before-add, repeat-task and
already-completed refusal, field validation (no line injection), single-parse
edits (no stale indices), freshness-checked temp-file + os.replace writes,
duplicate-metadata-key detection (surfaces union-merge artifacts: list flags them,
done refuses to edit them), and id-anchored post-write verification.

Usage:
  belki.py list [--all]
  belki.py summary [--days N]
  belki.py add [--] "Title" [--project P] [--due D] [--deadline D] [--priority Pn]
               [--description TEXT] [--labels a,b] [--claude] [--waiting-on WHO]

Waiting-on tasks (someone else owes it) carry `waiting_on:: WHO` plus the `waiting`
label. Belki's UI keeps unknown keys on save (serializeTaskLines -> extraProperties),
so the field survives UI edits. summary reports them in their own `waiting` list
(never in overdue/due_soon) and counts open undated tasks (`undated`).
  belki.py done [--] <task-id | unique title substring> [--dry-run]
  (use `--` before a title/query that starts with a dash)

Any inconsistency -> exit 2 with a message, file untouched. Exit 4 = the file
changed underneath us mid-operation (nothing was written -- just retry).
Never deletes tasks. Never touches repeat:: tasks.
"""
import argparse
import datetime as dt
import json
import os
import random
import re
import string
import sys
import tempfile
from pathlib import Path

# House rule: never crash on a cp1252 console (task titles may carry arrows/unicode).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

TASK_RE = re.compile(r"^- \[( |x)\] (.*)$")
META_RE = re.compile(r"^  (\w+):: ?(.*)$")


def die(msg: str, code: int = 2):
    print(f"belki.py: {msg}", file=sys.stderr)
    sys.exit(code)


def find_data_dir() -> Path:
    env = os.environ.get("BELKI_DIR")
    if env:
        p = Path(env)
        d = p if p.name == "Data" else p / "Data"
        if not d.is_dir():
            die(f"BELKI_DIR={env!r} resolved to {d} which is not a directory")
        return d
    cur = Path.cwd()
    for cand in [cur, *cur.parents]:
        d = cand / "_belki_files" / "Data"
        if d.is_dir():
            return d
    die("_belki_files/Data/ not found walking up from cwd (set BELKI_DIR to override)")


def read_and_parse(path: Path):
    """Return (raw_bytes, tasks) from ONE read. All edit indices must come from the
    same parse that produced the raw bytes being edited -- never mix generations.
    Task = title line index + contiguous 2-space `key:: value` block directly below;
    any other line (incl. blank) ends the block. Everything else is untouched context."""
    raw = path.read_bytes()
    if b"\r" in raw:
        die(f"{path.name} contains CR bytes -- refusing (LF-only store); fix line endings first")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        die(f"{path.name} is not valid UTF-8 ({e}) -- fix the file first")
    lines = text.split("\n")
    tasks, current = [], None
    for i, line in enumerate(lines):
        m = TASK_RE.match(line)
        if m:
            current = {"file": path, "line": i, "raw_line": line, "done": m.group(1) == "x",
                       "title": m.group(2).strip(), "meta": {}, "meta_lines": {},
                       "last_meta": i, "dup_keys": set()}
            tasks.append(current)
            continue
        if current is not None:
            mm = META_RE.match(line)
            if mm:
                key = mm.group(1)
                if key in current["meta"]:
                    current["dup_keys"].add(key)  # repeated key in one block: union-merge artifact
                current["meta"][key] = mm.group(2).strip()
                current["meta_lines"][key] = i
                current["last_meta"] = i
                continue
            current = None  # blank or any other line detaches -- block ends here
    return raw, tasks


def all_tasks(data_dir: Path):
    out = []
    for f in sorted(data_dir.glob("*.md")):
        _, tasks = read_and_parse(f)
        out.extend(tasks)
    return out


def atomic_write(path: Path, data: bytes, expected_old: bytes):
    """Freshness-checked atomic write: re-read immediately before replacing and
    refuse (exit 4, nothing written) if the file no longer matches the snapshot
    this edit was computed from -- surfaces concurrent Belki-UI/sync writes
    instead of silently clobbering them. (A microsecond race remains between the
    check and os.replace; the window was seconds before.) Verifies bytes after."""
    current = path.read_bytes() if path.exists() else b""
    if current != expected_old:
        die(f"{path.name} changed during the operation -- nothing written; retry", 4)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".belki-tmp-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    if path.read_bytes() != data:
        die(f"post-write verification FAILED for {path} -- inspect immediately", 3)


def gen_id(existing_ids: set) -> str:
    for _ in range(20):
        ts = format(int(dt.datetime.now().timestamp() * 1000), "x")
        rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        tid = f"task-{ts}-{rand}"
        if tid not in existing_ids:
            return tid
    die("could not generate a unique task id")


def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())


def check_field(name: str, value: str):
    if "\n" in value or "\r" in value:
        die(f"--{name} must be single-line (line injection refused)")


def check_date(name: str, value: str):
    check_field(name, value)
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        die(f"--{name} must be ISO YYYY-MM-DD, got {value!r}")


def parse_due(value: str):
    try:
        return dt.date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        return None


def task_due(t):
    """Shared due extraction for list/summary: due:: wins over deadline::.
    Returns (raw_string, parsed_date_or_None)."""
    due_raw = t["meta"].get("due") or t["meta"].get("deadline") or ""
    return due_raw, (parse_due(due_raw) if due_raw else None)


def task_project(t) -> str:
    """Shared project default: missing (or empty) project:: means Inbox."""
    return t["meta"].get("project") or "Inbox"


WAITING_STALE_DAYS = 7


def task_waiting(t) -> str:
    return (t["meta"].get("waiting_on") or "").strip()


def cmd_list(args):
    data_dir = find_data_dir()
    tasks = all_tasks(data_dir)
    today = dt.date.today()
    shown = 0
    for t in tasks:
        if t["done"] and not args.all:
            continue
        due_raw, due = task_due(t)
        flag = " !OVERDUE" if (due and not t["done"] and due < today) else ""
        proj = task_project(t)
        state = "x" if t["done"] else " "
        dup = f"  !DUPKEY({','.join(sorted(t['dup_keys']))})" if t["dup_keys"] else ""
        who = task_waiting(t)
        wait = f"  waiting:{who}" if who else ""
        print(f"[{state}] ({proj}) {t['title']}"
              f"{'  due:' + due_raw if due_raw else ''}{wait}{flag}{dup}  id={t['meta'].get('id', '?')}")
        shown += 1
    print(f"-- {shown} task(s) shown from {data_dir}")


def cmd_summary(args):
    """Read-only JSON digest for the /catchup glance: overdue + due-soon open tasks
    across ALL month files (files are keyed by CREATION month, so an overdue task
    can live in any file -- the --days window is a due-date window, not a file
    window). Writes nothing."""
    if args.days < 0:
        die(f"--days must be >= 0, got {args.days}")
    data_dir = find_data_dir()
    if not sorted(data_dir.glob("*.md")):
        die(f"no month files (*.md) found in {data_dir} -- wrong BELKI_DIR?")
    today = dt.date.today()
    horizon = today + dt.timedelta(days=args.days)
    overdue, due_soon, waiting, undated = [], [], [], 0
    for t in all_tasks(data_dir):
        if t["done"]:
            continue
        due_raw, due = task_due(t)
        who = task_waiting(t)
        if who:
            created = parse_due(t["meta"].get("created", ""))
            stale = (due < today) if due else bool(
                created and (today - created).days > WAITING_STALE_DAYS)
            waiting.append({"title": t["title"], "who": who, "project": task_project(t),
                            "due": due.isoformat() if due else "", "stale": stale})
            continue
        if due is None:
            if "repeat" not in t["meta"]:
                undated += 1
            continue
        item = {"title": t["title"], "due": due.isoformat(),
                "project": task_project(t)}
        if "repeat" in t["meta"]:
            # Recurring tasks keep their checkbox unchecked by design (the UI
            # tracks completions in completedOccurrences::), so a past due:: is
            # not necessarily "overdue" -- expose repeat so the caller discounts it.
            item["repeat"] = t["meta"]["repeat"]
        if due < today:
            overdue.append(item)
        elif due <= horizon:
            due_soon.append(item)
    overdue.sort(key=lambda x: x["due"])
    due_soon.sort(key=lambda x: x["due"])
    waiting.sort(key=lambda x: (not x["stale"], x["due"] or "9999"))
    # ensure_ascii keeps stdout ASCII-only (cp1252 console safety).
    print(json.dumps({"overdue": overdue, "due_soon": due_soon,
                      "waiting": waiting, "undated": undated},
                     ensure_ascii=True, indent=2))


def cmd_add(args):
    check_field("title", args.title)
    if TASK_RE.match(args.title) or args.title.strip() == "":
        die("title empty or looks like a task line itself -- refused")
    for name in ("project", "description", "labels", "waiting_on"):
        check_field(name, getattr(args, name))
    if args.due:
        check_date("due", args.due)
    if args.deadline:
        check_date("deadline", args.deadline)
    if not re.fullmatch(r"P[1-4]", args.priority):
        die(f"--priority must be P1..P4, got {args.priority!r}")

    data_dir = find_data_dir()
    tasks = all_tasks(data_dir)
    if not tasks:
        die("Data/ has no tasks yet -- create one in the Belki UI first (calibration prerequisite)")
    for t in tasks:
        if not t["done"] and norm_title(t["title"]) == norm_title(args.title) \
                and t["meta"].get("project", "") == (args.project or ""):
            die(f"duplicate: open task with the same title already exists (id={t['meta'].get('id')})")
    ids = {t["meta"].get("id") for t in tasks}
    tid = gen_id(ids)
    today = dt.date.today().isoformat()
    block = [f"- [ ] {args.title}", f"  id:: {tid}", f"  created:: {today}"]
    if args.due:
        block.append(f"  due:: {args.due}")
    if args.deadline:
        block.append(f"  deadline:: {args.deadline}")
    if args.project:
        block.append(f"  project:: {args.project}")
    block.append(f"  priority:: {args.priority}")
    if args.description:
        block.append(f"  description:: {args.description}")
    labels = [x.strip() for x in (args.labels.split(",") if args.labels else []) if x.strip()]
    if args.claude and "claude" not in labels:
        labels.append("claude")
    if args.waiting_on.strip() and "waiting" not in labels:
        labels.append("waiting")
    if labels:
        block.append(f"  labels:: {', '.join(labels)}")
    if args.waiting_on.strip():
        block.append(f"  waiting_on:: {args.waiting_on.strip()}")

    target = data_dir / (dt.date.today().strftime("%Y-%m") + ".md")
    old = target.read_bytes() if target.exists() else b""
    if b"\r" in old:
        die(f"{target.name} contains CR bytes -- refusing (LF-only store); fix line endings first")
    new = old
    if new and not new.endswith(b"\n"):
        new += b"\n"
    new += ("\n".join(block) + "\n").encode("utf-8")
    if not new.startswith(old):
        die("internal error: append would not preserve existing bytes", 3)
    atomic_write(target, new, old)
    _, after = read_and_parse(target)
    hits = [t for t in after if t["meta"].get("id") == tid]
    if len(hits) != 1 or hits[0]["title"] != args.title.strip():
        die("post-write parse check FAILED -- new task not readable as written", 3)
    print(f"added {tid}: {args.title}  ({target.name})")


def cmd_done(args):
    data_dir = find_data_dir()
    # Resolve the task id first (cheap scan may use any parse generation)...
    open_tasks = [t for t in all_tasks(data_dir) if not t["done"]]
    matches = [t for t in open_tasks if t["meta"].get("id") == args.task]
    if not matches:
        matches = [t for t in open_tasks if args.task.lower() in t["title"].lower()]
    if not matches:
        die(f"no open task matches {args.task!r}")
    if len(matches) > 1:
        for t in matches:
            print(f"  candidate: {t['title']}  id={t['meta'].get('id')}", file=sys.stderr)
        die("ambiguous match -- rerun with the exact id")
    tid = matches[0]["meta"].get("id")
    path = matches[0]["file"]
    if not tid:
        die("matched task has no id:: in its attached metadata (detached block / blank line?) -- fix it in the Belki UI first")

    # ...then do the EDIT against one fresh parse: indices and bytes from the same read.
    raw, tasks = read_and_parse(path)
    hits = [t for t in tasks if t["meta"].get("id") == tid]
    if len(hits) != 1:
        die(f"id {tid} appears {len(hits)}x in {path.name} (sync-merge duplicate?) -- fix manually first")
    t = hits[0]
    if t["done"]:
        die(f"task {tid} is already completed")
    if "repeat" in t["meta"]:
        die("task has repeat:: -- recurring completion belongs to the Belki UI, refusing")
    if "completed" in t["meta"]:
        die(f"open task already carries completed:: ({t['meta']['completed']}) -- reopened in the UI? fix there first")
    if t["dup_keys"]:
        die(f"task {tid} has duplicate metadata key(s) {sorted(t['dup_keys'])} "
            "(cross-device union-merge artifact?) -- fix manually first")
    lines = raw.decode("utf-8").split("\n")
    if lines[t["line"]] != t["raw_line"] or not lines[t["line"]].startswith("- [ ] "):
        die("task line mismatch against fresh parse -- internal error, nothing written", 3)
    if args.dry_run:
        print(f"DRY RUN: would complete {tid} in {path.name}")
        return
    lines[t["line"]] = "- [x] " + lines[t["line"]][len("- [ ] "):]
    lines.insert(t["last_meta"] + 1, f"  completed:: {dt.date.today().isoformat()}")
    new = "\n".join(lines).encode("utf-8")
    atomic_write(path, new, raw)
    _, after = read_and_parse(path)
    done_t = [x for x in after if x["meta"].get("id") == tid]
    if len(done_t) != 1 or not done_t[0]["done"] or "completed" not in done_t[0]["meta"]:
        die("post-write verification FAILED -- inspect the file", 3)
    print(f"completed {tid}: {t['title']}  ({path.name})")


def main():
    ap = argparse.ArgumentParser(
        prog="belki.py",
        epilog="Titles/queries starting with '-' need the '--' separator: belki.py add -- \"-my title\"")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("summary"); p.add_argument("--days", type=int, default=7); p.set_defaults(fn=cmd_summary)
    p = sub.add_parser("add"); p.add_argument("title")
    p.add_argument("--project", default=""); p.add_argument("--due", default="")
    p.add_argument("--deadline", default=""); p.add_argument("--priority", default="P4")
    p.add_argument("--description", default=""); p.add_argument("--labels", default="")
    p.add_argument("--claude", action="store_true"); p.add_argument("--waiting-on", default="")
    p.set_defaults(fn=cmd_add)
    p = sub.add_parser("done"); p.add_argument("task"); p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_done)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
