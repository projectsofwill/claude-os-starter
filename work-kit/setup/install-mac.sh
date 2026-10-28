#!/usr/bin/env bash
# Mac setup for the work brain: mods, Claude settings, statusline, VS Code launcher + keybindings.
# Safe to re-run: every step checks first, existing settings keys and key bindings are never replaced, and every
# JSON file it edits is backed up, then rewritten via parse -> temp -> re-parse -> atomic replace.
# Usage: setup/install-mac.sh [--dry-run]
set -u

DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1
BRAIN="$(cd "$(dirname "$0")/.." && pwd)"
SETUP="$BRAIN/setup"
VSUSER="$HOME/Library/Application Support/Code/User"
EXT_DIR="$HOME/.vscode/extensions/work-kit.claude-launcher-0.1.0"
RESULTS=()

note() { RESULTS+=("$1  $2"); }
run() { if [ "$DRY" = 1 ]; then echo "DRY RUN: $*"; else "$@"; fi; }

# ---- 1. prerequisites
PY=""
for c in python3 python; do
  if "$c" -c "" >/dev/null 2>&1; then PY="$c"; break; fi
done
command -v claude >/dev/null && note "[ok]  " "claude found" || note "[FAIL]" "claude not found: install Claude Code first"
[ -n "$PY" ] && note "[ok]  " "python: $PY" || note "[FAIL]" "no working python3 (hooks and /todo need it: xcode-select --install or brew install python)"
command -v jq >/dev/null && note "[ok]  " "jq found" || note "[warn]" "jq missing: the statusline needs it (brew install jq)"
[ -d "/Applications/Obsidian.app" ] && note "[ok]  " "Obsidian found" || note "[warn]" "Obsidian missing: Belki's UI needs it (then Settings > Community plugins > install 'belki', open $BRAIN as a vault)"

# ---- 2. mods marketplace + every listed mod
if command -v claude >/dev/null; then
  if claude plugin marketplace list 2>/dev/null | grep -q "work-mods"; then
    note "[ok]  " "marketplace work-mods already added"
  else
    run claude plugin marketplace add "$SETUP/mods" && note "[ok]  " "marketplace work-mods added"
  fi
  if [ -n "$PY" ]; then
    for m in $("$PY" -c 'import json,sys;print(" ".join(p["name"] for p in json.load(open(sys.argv[1]))["plugins"]))' "$SETUP/mods/.claude-plugin/marketplace.json"); do
      if run claude plugin install "$m@work-mods" >/dev/null 2>&1; then note "[ok]  " "mod $m"; else note "[FAIL]" "mod $m (run: claude plugin install $m@work-mods)"; fi
    done
  fi
fi

# ---- 3. statusline script
if [ -e "$HOME/.claude/statusline.sh" ]; then
  note "[ok]  " "statusline.sh exists (left as is)"
else
  run mkdir -p "$HOME/.claude" && run cp "$SETUP/claude/statusline.sh" "$HOME/.claude/statusline.sh" && run chmod +x "$HOME/.claude/statusline.sh" && note "[ok]  " "statusline.sh installed"
fi

# ---- 4. JSON merges (only missing keys/entries are added)
merge() {  # merge <target> <mode> <payload-json>
  [ -z "$PY" ] && { note "[FAIL]" "$1 not changed: no python"; return; }
  "$PY" - "$1" "$2" "$3" "$DRY" <<'PYEOF'
import json, os, shutil, sys, tempfile, time
target, mode, payload, dry = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), sys.argv[4] == "1"
default = [] if mode == "list" else {}
raw = open(target, encoding="utf-8").read() if os.path.exists(target) else ""
try:
    cur = json.loads(raw) if raw.strip() else default
except ValueError:
    # VS Code seeds keybindings.json with full-line // comments: drop those (the backup keeps them).
    try:
        cur = json.loads("\n".join(l for l in raw.splitlines() if not l.lstrip().startswith("//")))
        print(f"note: full-line // comments in {target} are dropped (kept in the .bak copy)")
    except ValueError:
        print(f"SKIP {target}: not plain JSON. Add these by hand: {json.dumps(payload)}")
        sys.exit(3)
added = []
if mode == "list":
    # A key already bound to anything is left alone: appending would override the existing behavior.
    taken = {e.get("key") for e in cur if isinstance(e, dict)}
    for e in payload:
        if e["key"] in taken:
            print(f"note: {e['key']} is already bound in {target}; left as is (kit binding: {json.dumps(e)})")
        else:
            cur.append(e); added.append(e["key"])
else:
    def deep(dst, src, path=""):
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                deep(dst[k], v, path + k + ".")
            elif k not in dst:
                dst[k] = v; added.append(path + k)
    deep(cur, payload)
if not added:
    print(f"unchanged {target}"); sys.exit(0)
if dry:
    print(f"DRY RUN: would add {added} to {target}"); sys.exit(0)
os.makedirs(os.path.dirname(target), exist_ok=True)
if os.path.exists(target):
    shutil.copy2(target, f"{target}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(target), prefix=".tmp-")
with os.fdopen(fd, "w", encoding="utf-8") as fh:
    json.dump(cur, fh, indent=2); fh.write("\n")
json.load(open(tmp, encoding="utf-8"))
os.replace(tmp, target)
print(f"added {added} to {target}")
PYEOF
  case $? in
    0) note "[ok]  " "$(basename "$(dirname "$1")")/$(basename "$1") merged" ;;
    3) note "[warn]" "$1 has comments: add the entries by hand (see output above)" ;;
    *) note "[FAIL]" "$1 not changed" ;;
  esac
}

CLAUDE_PAYLOAD=$("${PY:-python3}" -c 'import json,sys; b=sys.argv[1]; print(json.dumps({
  "env": {"CLAUDE_CODE_ENABLE_FUNCTION_HOOKS": "1",
          "BELKI_HELPER": b + "/.claude/skills/todo/scripts/belki.py",
          "WORK_BRAIN_DIR": b},
  "statusLine": {"type": "command", "command": "bash ~/.claude/statusline.sh"}}))' "$BRAIN" 2>/dev/null || echo '{}')
merge "$HOME/.claude/settings.json" dict "$CLAUDE_PAYLOAD"
merge "$VSUSER/settings.json" dict "$(cat "$SETUP/vscode/user-settings.json")"
merge "$VSUSER/keybindings.json" list "$(cat "$SETUP/vscode/keybindings.json")"

# ---- 5. VS Code launcher extension (local, unpacked)
if [ -d "$EXT_DIR" ]; then
  note "[ok]  " "launcher extension already installed ($EXT_DIR)"
else
  run mkdir -p "$EXT_DIR" && run cp "$SETUP/vscode/claude-launcher/package.json" "$SETUP/vscode/claude-launcher/extension.js" "$EXT_DIR/" \
    && note "[ok]  " "launcher extension installed (reload VS Code)"
fi
if [ -d "$VSUSER/profiles" ] && [ -n "$(ls -A "$VSUSER/profiles" 2>/dev/null)" ]; then
  note "[warn]" "VS Code profiles exist: if you use a non-default profile, copy setup/vscode/keybindings.json into that profile's keybindings.json"
fi

# ---- 6. one memory store: Claude Code's auto-memory dir for this repo -> the repo's memory/
# (the harness and the reflect mod write to ~/.claude/projects/<path slug>/memory; the router reads memory/)
SLUG="$(printf '%s' "$BRAIN" | sed 's/[^a-zA-Z0-9]/-/g')"
AUTOMEM="$HOME/.claude/projects/$SLUG/memory"
if [ -L "$AUTOMEM" ]; then
  note "[ok]  " "auto-memory already linked to $(readlink "$AUTOMEM")"
elif [ -e "$AUTOMEM" ]; then
  note "[warn]" "auto-memory dir exists as a real folder: move its files into $BRAIN/memory/, delete it, re-run"
else
  run mkdir -p "$(dirname "$AUTOMEM")" && run ln -s "$BRAIN/memory" "$AUTOMEM" && note "[ok]  " "auto-memory -> $BRAIN/memory"
fi

echo
echo "Work brain setup ($BRAIN)$([ "$DRY" = 1 ] && echo ' [dry run]')"
for r in "${RESULTS[@]}"; do echo "  $r"; done
echo "Next: open $BRAIN in VS Code (Claude auto-launches) and as an Obsidian vault (Belki)."
