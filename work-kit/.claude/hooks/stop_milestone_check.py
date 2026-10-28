#!/usr/bin/env python3
"""
Stop hook: milestone check + unverified-claim check (work brain, .claude/settings.json).

Uses the one Stop-hook channel that reaches the model, `{"decision": "block", "reason": ...}`,
which makes Claude take ONE more short turn. `Stop` fires after every reply, so two gates keep
it to the right moments:

1. Milestone check: fires only on a turn that ran `git commit`. If the commits touched work
   files but no STATUS.md (root or projects/*/STATUS.md), asks for a STATUS refresh.
   Commits that only touch handoff docs (STATUS.md / index.md / Belki task files) don't count, so the
   follow-up commit this hook causes doesn't re-trigger it. Deduped per (session, commit set).

2. Unverified-claim check: fires when the final reply claims "tested / verified / tests pass"
   but no Bash ran this turn. Capped at 2 per session.

Both results go out as ONE block. `stop_hook_active` short-circuits everything, so it can
never loop. Fails OPEN on any error: a hook bug must never break or trap a session.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime

try:
    from _nudge_dedupe import should_fire
except Exception:
    def should_fire(kind, session_id, subkey=""):
        return True

_MSYS = re.compile(r"^/([a-zA-Z])/")

GIT_COMMIT = re.compile(r"\bgit\b[^\n;&|]*\bcommit\b")
CLAIM = re.compile(
    r"\b(tested|verified|tests? pass(?:es|ed)?|all green|confirmed working|works now)\b", re.I)
NEGATION = re.compile(
    r"\b(un(?:tested|verified)|not (?:yet )?(?:tested|verified)|(?:haven't|hasn't|didn't|did not|"
    r"couldn't|could not) (?:test|verify|run))\b", re.I)
HANDOFF_DOCS = ("status.md", "index.md")
MAX_CLAIM_NUDGES = 2


def _winpath(p):
    if not p or os.name != "nt":
        return p
    return _MSYS.sub(lambda m: m.group(1).upper() + ":/", p)


def _git(repo, *args, timeout=3):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return r.stdout if r.returncode == 0 else ""


def _rows(path):
    path = _winpath(path)
    if os.path.getsize(path) > 50 * 1024 * 1024:
        return []
    out = []
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def _is_prompt(row):
    """A real user prompt (not a tool result, not injected meta)."""
    if row.get("type") != "user" or row.get("isMeta"):
        return False
    c = (row.get("message") or {}).get("content")
    if isinstance(c, str):
        return True
    return isinstance(c, list) and any(
        isinstance(i, dict) and i.get("type") == "text" for i in c)


def _tool_uses(row, with_id=False):
    if row.get("type") != "assistant":
        return
    c = (row.get("message") or {}).get("content")
    for i in c if isinstance(c, list) else []:
        if isinstance(i, dict) and i.get("type") == "tool_use":
            if with_id:
                yield i.get("id", ""), i.get("name", ""), (i.get("input") or {})
            else:
                yield i.get("name", ""), (i.get("input") or {})


def _last_text(rows):
    for row in reversed(rows):
        if row.get("type") != "assistant":
            continue
        c = (row.get("message") or {}).get("content")
        texts = [i.get("text", "") for i in c if isinstance(i, dict) and i.get("type") == "text"] \
            if isinstance(c, list) else []
        if texts:
            return "\n".join(texts)
    return ""


def _epoch(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _commits_since(repo, since):
    """[(sha, [files])] for commits after `since` (epoch seconds)."""
    out = _git(repo, "log", f"--since=@{int(since)}", "--no-merges",
               "--format=@@%H%x09%s", "--name-only")
    commits, cur = [], None
    for line in out.splitlines():
        if line.startswith("@@"):
            cur = (line[2:].partition("\t")[0], [])
            commits.append(cur)
        elif line.strip() and cur:
            cur[1].append(line.strip())
    return commits


def milestone_reasons(root, turn_rows, session_id):
    turn_cmds = [ti.get("command", "") for r in turn_rows for n, ti in _tool_uses(r) if n == "Bash"]
    if not any(GIT_COMMIT.search(c) for c in turn_cmds):
        return []
    start = next((_epoch(r.get("timestamp", "")) for r in turn_rows if _is_prompt(r)), None)
    if start is None:
        return []
    every = _commits_since(root, start - 5)  # 5s clock slack
    commits = [(s, f) for s, f in every
               if any(os.path.basename(x).lower() not in HANDOFF_DOCS
                      and not x.startswith("_belki_files/") for x in f)]
    if not commits:
        return []
    touched = {os.path.basename(x).lower() for _, f in every for x in f}
    turn_edited = {(ti.get("file_path") or "").replace("\\", "/").lower()
                   for r in turn_rows for n, ti in _tool_uses(r) if n in ("Edit", "Write")}
    if "status.md" in touched or any(p.endswith("status.md") for p in turn_edited):
        return []
    if not should_fire("milestone", session_id, ",".join(sorted(s for s, _ in commits))):
        return []
    return ["Work was committed but no STATUS.md was refreshed: update the workstream's "
            "projects/<name>/STATUS.md ## Now / ## Next (append any ## Decisions) and its line "
            "in root STATUS.md."]


def claim_reason(turn_rows, session_id):
    text = _last_text(turn_rows)
    if not CLAIM.search(text) or NEGATION.search(text):
        return []
    if any(n == "Bash" for r in turn_rows for n, _ in _tool_uses(r)):
        return []
    for i in range(MAX_CLAIM_NUDGES):
        if should_fire("claim", session_id, str(i)):
            return ["Your reply claims something was tested/verified, but no command ran this turn. "
                    "Run it now, or reword to say it's unverified (if you mean an earlier turn's "
                    "check, name the command and result in one line)."]
    return []


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    if data.get("stop_hook_active") or not data.get("transcript_path"):
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ""
    sid = data.get("session_id")
    try:
        rows = _rows(data["transcript_path"])
        last_prompt = max((i for i, r in enumerate(rows) if _is_prompt(r)), default=None)
        if last_prompt is None:
            return
        turn = rows[last_prompt:]
        reasons = claim_reason(turn, sid)
        if root and os.path.isdir(root):
            reasons += milestone_reasons(root, turn, sid)
    except Exception:
        return
    if reasons:
        print(json.dumps({"decision": "block", "reason":
                          "Stop-hook check. Do these briefly, then stop (skip any that don't apply):\n- "
                          + "\n- ".join(reasons)}))


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
