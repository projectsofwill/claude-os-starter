// Launch Claude Code (terminal mode) on workspace open via the Claude extension's own
// launcher, so it opens as an editor tab like clicking the icon. Resumes the last session
// for the folder only if it was active recently: past ~1h the prompt cache is cold and a
// big resumed session reprocesses uncached.
// Also adds a Tasks section to the Claude Code sidebar: Belki tasks from this workspace via the
// /todo skill's helper (overdue, due this week, waiting-on to chase, then open tasks by project).
const vscode = require("vscode");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFile } = require("child_process");

// Newest transcript mtime for this folder (Claude stores them under ~/.claude/projects/<cwd with non-alnum -> ->).
function lastSessionMs(cwd) {
  const key = cwd.replace(/[^a-zA-Z0-9]/g, "-").toLowerCase();
  const root = path.join(os.homedir(), ".claude", "projects");
  let newest = 0;
  try {
    for (const d of fs.readdirSync(root)) {
      if (d.toLowerCase() !== key) continue;
      for (const f of fs.readdirSync(path.join(root, d))) {
        if (f.endsWith(".jsonl")) newest = Math.max(newest, fs.statSync(path.join(root, d, f)).mtimeMs);
      }
    }
  } catch {}
  return newest;
}

async function launch() {
  const cfg = vscode.workspace.getConfiguration("claudeLauncher");
  const folder = vscode.workspace.workspaceFolders?.[0];
  if (!folder || !cfg.get("autoLaunch")) return;
  const idleMin = (Date.now() - lastSessionMs(folder.uri.fsPath)) / 60000;
  const args = idleMin < cfg.get("resumeWithinMinutes", 60) ? ["--continue"] : [];
  // claude-vscode.terminal.open(prompt?, args?, location?) -> runs `claude <args>` in an editor-area terminal
  await vscode.commands.executeCommand("claude-vscode.terminal.open", undefined, args);
  // Claude terminals are transient (not restored), so last session's terminal groups come back
  // empty. Sweep them once the new Claude tab lands; before that, on a fresh start every group is
  // empty and none can close (VS Code keeps at least one).
  for (let i = 0; i < 40 && vscode.window.tabGroups.all.every((g) => g.tabs.length === 0); i++) {
    await new Promise((r) => setTimeout(r, 250));
  }
  const empty = vscode.window.tabGroups.all.filter((g) => g.tabs.length === 0);
  if (empty.length && empty.length < vscode.window.tabGroups.all.length) await vscode.window.tabGroups.close(empty);
}

// The /todo helper lives in the workspace (project-scoped skill); it finds _belki_files by walking up from cwd.
// It is repo code, so it only runs in a folder that carries the work brain's `.work-brain` marker.
function belki(args) {
  const cwd = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!cwd) return Promise.reject(new Error("no workspace folder"));
  if (!fs.existsSync(path.join(cwd, ".work-brain"))) return Promise.reject(new Error("not a work brain (no .work-brain marker)"));
  const script = path.join(cwd, ".claude", "skills", "todo", "scripts", "belki.py");
  const py = process.platform === "win32" ? "python" : "python3";
  return new Promise((resolve, reject) =>
    execFile(py, [script, ...args], { cwd, timeout: 30000, env: { ...process.env, PYTHONIOENCODING: "utf-8" } }, (err, out) =>
      err ? reject(err) : resolve(out)
    )
  );
}

function group(label, children, icon, expanded) {
  const item = new vscode.TreeItem(label, expanded ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.Collapsed);
  item.description = String(children.length);
  item.iconPath = new vscode.ThemeIcon(icon);
  item.children = children;
  return item;
}

function taskItem(title, detail) {
  const item = new vscode.TreeItem(title);
  item.description = detail;
  item.tooltip = detail ? `${title}\n${detail}` : title;
  return item;
}

class TasksProvider {
  constructor() {
    this._emitter = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._emitter.event;
  }
  refresh() {
    this._emitter.fire();
  }
  getTreeItem(item) {
    return item;
  }
  async getChildren(parent) {
    if (parent) return parent.children;
    try {
      const [summary, list] = await Promise.all([belki(["summary", "--days", "7"]), belki(["list"])]);
      const { overdue, due_soon, waiting = [], undated = 0 } = JSON.parse(summary);
      const groups = [];
      const dated = (t) => taskItem(t.title, `${t.project} · ${t.due}${t.repeat ? " · repeats" : ""}`);
      if (overdue.length) groups.push(group("Overdue", overdue.map(dated), "warning", true));
      if (due_soon.length) groups.push(group("Due this week", due_soon.map(dated), "calendar", true));
      const chase = waiting.filter((t) => t.stale);
      if (chase.length) groups.push(group("Chase", chase.map((t) => taskItem(`${t.who}: ${t.title}`, t.due || "no date")), "bell", true));
      const rest = waiting.filter((t) => !t.stale);
      if (rest.length) groups.push(group("Waiting on", rest.map((t) => taskItem(`${t.who}: ${t.title}`, t.due || "no date")), "watch", false));
      // list lines: "[ ] (Project) Title  due:...  waiting:...  id=task-..."; waiting items are shown above.
      const byProject = new Map();
      for (const m of list.matchAll(/^\[ \] \((.+?)\) (.+?)(?:\s+due:\S+)?(\s+waiting:.+?)?(?:\s+!OVERDUE)?\s+id=\S+$/gm)) {
        if (m[3]) continue;
        if (!byProject.has(m[1])) byProject.set(m[1], []);
        byProject.get(m[1]).push(taskItem(m[2]));
      }
      for (const [p, items] of [...byProject].sort(([a], [b]) => (a === "Inbox") - (b === "Inbox") || a.localeCompare(b))) {
        groups.push(group(p, items, "folder", false));
      }
      if (undated) groups.push(taskItem(`${undated} task(s) without a due date`, "run /todo sweep"));
      return groups.length ? groups : [new vscode.TreeItem("No open tasks")];
    } catch (e) {
      const item = new vscode.TreeItem(/no \.work-brain marker/.test(String(e.message)) ? "Not a work brain" : "Belki unavailable");
      item.tooltip = String(e.message || e);
      item.iconPath = new vscode.ThemeIcon("error");
      return [item];
    }
  }
}

exports.activate = (context) => {
  const tasks = new TasksProvider();
  // One view per Claude sidebar container; only the container Claude currently shows is visible.
  for (const suffix of ["", "Secondary", "Sessions"]) {
    context.subscriptions.push(vscode.window.registerTreeDataProvider(`claudeLauncher.tasks${suffix}`, tasks));
  }
  const timer = setInterval(() => tasks.refresh(), 5 * 60000);
  context.subscriptions.push(
    { dispose: () => clearInterval(timer) },
    vscode.commands.registerCommand("claudeLauncher.refreshTasks", () => tasks.refresh())
  );
  return launch();
};
exports.deactivate = () => {};
