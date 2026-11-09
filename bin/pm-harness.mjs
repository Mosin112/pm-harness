#!/usr/bin/env node
// PM Harness installer: puts the harness into a PM workspace for any AI tool.
//
//   npx github:Mosin112/pm-harness init     install into this folder
//   npx github:Mosin112/pm-harness update   refresh the harness files, keep your work
//   npx github:Mosin112/pm-harness doctor   check an installation
//
// No dependencies; Node 18 or later. Files the PM owns (context, decisions, work) are created
// once and never overwritten. Files the harness owns (skills, checker, reference) are tracked
// in .pm-harness/install.json so updates can replace them and spot local edits.

import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));
const MARKER = "pm-harness-workspace";
const BEGIN = "<!-- pm-harness:begin -->";
const END = "<!-- pm-harness:end -->";
const MARKETPLACE = "Mosin112/pm-harness";
const PLUGIN_ID = "pm-harness@pm-harness";

export const TOOLS = [
  { id: "claude-code", label: "Claude Code", skills: ".claude/skills" },
  { id: "codex", label: "Codex", skills: ".agents/skills" },
  { id: "cursor", label: "Cursor", skills: ".agents/skills" },
  { id: "copilot", label: "GitHub Copilot", skills: ".agents/skills" },
  { id: "gemini", label: "Gemini CLI", skills: ".agents/skills" },
  { id: "other", label: "Another tool that reads AGENTS.md", skills: ".agents/skills" },
];

// ------------------------------------------------------------------ helpers

const sha = (buf) => createHash("sha256").update(buf).digest("hex");
const posix = (p) => p.split(path.sep).join("/");
const exists = (p) => fs.existsSync(p);
const readText = (p) => fs.readFileSync(p, "utf8");

function walk(dir, base = dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.name === ".DS_Store" || entry.name === "__pycache__") continue;
    if (entry.isDirectory()) out.push(...walk(full, base));
    else out.push(posix(path.relative(base, full)));
  }
  return out.sort();
}

// Skills refer to the plugin root as ../../ ; installed skills sit one level deeper, next to
// the harness files in .pm-harness/.
export function rewriteSkill(text) {
  return text.replace(/\.\.\/\.\.\/(scripts\/pm_check\.py)?/g, (_, checker) =>
    checker ? "../../../.pm-harness/pm_check.py" : "../../../.pm-harness/");
}

function managedBlock() {
  const t = readText(path.join(ROOT, "templates/workspace/AGENTS.md"));
  return t.slice(t.indexOf(BEGIN), t.indexOf(END) + END.length);
}

export function withBlock(text) {
  const block = managedBlock();
  if (text.includes(BEGIN) && text.includes(END)) {
    return text.slice(0, text.indexOf(BEGIN)) + block + text.slice(text.indexOf(END) + END.length);
  }
  return text.replace(/\s*$/, "\n\n") + block + "\n";
}

function which(cmd) {
  const r = spawnSync(process.platform === "win32" ? "where" : "which", [cmd], { encoding: "utf8" });
  return r.status === 0;
}

function python() {
  for (const cmd of ["python3", "python"]) {
    const r = spawnSync(cmd, ["-c", "import sys; print('%d.%d' % sys.version_info[:2])"], { encoding: "utf8" });
    if (r.status === 0) {
      const [maj, min] = r.stdout.trim().split(".").map(Number);
      return { cmd, version: r.stdout.trim(), ok: maj === 3 && min >= 8 };
    }
  }
  return null;
}

// ------------------------------------------------------------------ the plan

// Managed files: path in the workspace -> Buffer contents.
export function managedFiles(tools, claudeMode) {
  const files = new Map();
  const add = (rel, data) => files.set(rel, Buffer.isBuffer(data) ? data : Buffer.from(data));
  add(".pm-harness/pm_check.py", fs.readFileSync(path.join(ROOT, "scripts/pm_check.py")));
  for (const dir of ["reference", "agents", "examples", "templates"]) {
    for (const rel of walk(path.join(ROOT, dir))) {
      add(`.pm-harness/${dir}/${rel}`, fs.readFileSync(path.join(ROOT, dir, rel)));
    }
  }
  const skillDirs = new Set();
  for (const id of tools) {
    const tool = TOOLS.find((t) => t.id === id);
    if (!tool) continue;
    if (id === "claude-code" && claudeMode !== "files") continue;
    skillDirs.add(tool.skills);
  }
  for (const target of skillDirs) {
    for (const rel of walk(path.join(ROOT, "skills"))) {
      const src = fs.readFileSync(path.join(ROOT, "skills", rel));
      add(`${target}/${rel}`, rel.endsWith(".md") ? rewriteSkill(src.toString("utf8")) : src);
    }
  }
  if (tools.includes("claude-code") && claudeMode === "files") {
    for (const rel of walk(path.join(ROOT, "agents"))) {
      add(`.claude/agents/${rel}`, fs.readFileSync(path.join(ROOT, "agents", rel)));
    }
  }
  return files;
}

// Seed files: created once if missing, never overwritten.
function seedFiles(tools) {
  const seeds = new Map();
  const tpl = path.join(ROOT, "templates/workspace");
  for (const rel of walk(tpl)) {
    if (rel === "AGENTS.md" || rel === "CLAUDE.md") continue;
    if (rel.startsWith(".claude/") && !tools.includes("claude-code")) continue;
    seeds.set(rel, fs.readFileSync(path.join(tpl, rel)));
  }
  return seeds;
}

const SESSION_HOOK = {
  hooks: [{ type: "command", command: 'python3 "$CLAUDE_PROJECT_DIR/.pm-harness/pm_check.py" board "$CLAUDE_PROJECT_DIR"', timeout: 10 }],
};

export function plan(ws, opts) {
  const { tools, claudeMode } = opts;
  const steps = [];
  const tplDir = path.join(ROOT, "templates/workspace");
  const agentsPath = path.join(ws, "AGENTS.md");
  const claudePath = path.join(ws, "CLAUDE.md");
  const claudeText = exists(claudePath) ? readText(claudePath) : null;
  const claudeIsStub = claudeText !== null && /^\s*(<!--[^>]*-->\s*)?@AGENTS\.md\s*$/m.test(claudeText) && claudeText.trim().split("\n").length <= 3;

  // AGENTS.md: the canonical workspace file every tool reads.
  if (exists(agentsPath)) {
    const current = readText(agentsPath);
    const next = current.includes(MARKER) ? withBlock(current) : withBlock(current.replace(/\s*$/, "\n\n") + readText(path.join(tplDir, "AGENTS.md")).split(BEGIN)[0].trim() + "\n");
    if (next !== current) steps.push({ kind: "write", rel: "AGENTS.md", data: next, note: current.includes(MARKER) ? "refresh the PM Harness block" : "add the PM workspace section to your AGENTS.md" });
  } else if (claudeText && claudeText.includes(MARKER) && !claudeIsStub) {
    // A 0.1 workspace keeps everything in CLAUDE.md: move it to AGENTS.md so every tool reads it.
    steps.push({ kind: "write", rel: "AGENTS.md", data: withBlock(claudeText), note: "move your CLAUDE.md content here so every tool can read it" });
    steps.push({ kind: "write", rel: "CLAUDE.md", data: readText(path.join(tplDir, "CLAUDE.md")), note: "now imports AGENTS.md" });
  } else {
    steps.push({ kind: "write", rel: "AGENTS.md", data: readText(path.join(tplDir, "AGENTS.md")), note: "workspace rules and routing" });
  }
  if (tools.includes("claude-code") && !steps.some((s) => s.rel === "CLAUDE.md")) {
    if (claudeText === null) {
      steps.push({ kind: "write", rel: "CLAUDE.md", data: readText(path.join(tplDir, "CLAUDE.md")), note: "imports AGENTS.md for Claude Code" });
    } else if (!/@AGENTS\.md/.test(claudeText)) {
      steps.push({ kind: "write", rel: "CLAUDE.md", data: claudeText.replace(/\s*$/, "\n\n") + "<!-- pm-harness-workspace -->\n@AGENTS.md\n", note: "add an import of AGENTS.md" });
    }
  }
  if (tools.includes("gemini")) {
    const gp = path.join(ws, "GEMINI.md");
    const gt = exists(gp) ? readText(gp) : null;
    if (gt === null) steps.push({ kind: "write", rel: "GEMINI.md", data: "@./AGENTS.md\n", note: "imports AGENTS.md for Gemini CLI" });
    else if (!gt.includes("AGENTS.md")) steps.push({ kind: "write", rel: "GEMINI.md", data: gt.replace(/\s*$/, "\n\n") + "@./AGENTS.md\n", note: "add an import of AGENTS.md" });
  }

  // Seed files the PM owns.
  for (const [rel, data] of seedFiles(tools)) {
    if (!exists(path.join(ws, rel))) steps.push({ kind: "seed", rel, data });
  }

  // Claude Code project files: register the session-start board hook.
  if (tools.includes("claude-code") && claudeMode === "files") {
    const sp = path.join(ws, ".claude/settings.json");
    const pending = steps.find((s) => s.rel === ".claude/settings.json");
    const base = pending ? JSON.parse(pending.data.toString()) : exists(sp) ? JSON.parse(readText(sp)) : {};
    const has = JSON.stringify(base.hooks?.SessionStart || []).includes("pm_check.py");
    if (!has) {
      base.hooks = base.hooks || {};
      base.hooks.SessionStart = [...(base.hooks.SessionStart || []), SESSION_HOOK];
      const data = JSON.stringify(base, null, 2) + "\n";
      if (pending) pending.data = Buffer.from(data);
      else steps.push({ kind: "write", rel: ".claude/settings.json", data, note: "show the pipeline board at session start" });
    }
  }

  // Managed harness files.
  const manifest = readManifest(ws);
  const managed = managedFiles(tools, claudeMode);
  for (const [rel, data] of managed) {
    const full = path.join(ws, rel);
    if (!exists(full)) { steps.push({ kind: "managed", rel, data, change: "add" }); continue; }
    const current = fs.readFileSync(full);
    if (sha(current) === sha(data)) continue;
    const recorded = manifest?.files?.[rel];
    const edited = recorded ? sha(current) !== recorded : true;
    steps.push({ kind: "managed", rel, data, change: "update", edited });
  }
  for (const rel of Object.keys(manifest?.files || {})) {
    if (managed.has(rel)) continue;
    const full = path.join(ws, rel);
    if (!exists(full)) continue;
    const edited = sha(fs.readFileSync(full)) !== manifest.files[rel];
    steps.push({ kind: "remove", rel, edited });
  }

  if (tools.includes("claude-code") && claudeMode === "plugin") {
    steps.push({ kind: "run", cmd: ["claude", "plugin", "marketplace", "add", MARKETPLACE] });
    steps.push({ kind: "run", cmd: ["claude", "plugin", "install", PLUGIN_ID] });
  }
  return { steps, managed };
}

function readManifest(ws) {
  const p = path.join(ws, ".pm-harness/install.json");
  try { return JSON.parse(readText(p)); } catch { return null; }
}

// ------------------------------------------------------------------ apply

function describe(steps, force) {
  const lines = [];
  const group = (title, items) => { if (items.length) { lines.push(title); lines.push(...items.map((s) => "  " + s)); } };
  group("Workspace files:", steps.filter((s) => s.kind === "write").map((s) => `${s.rel}  (${s.note})`));
  const seeds = steps.filter((s) => s.kind === "seed").map((s) => s.rel);
  group("Create once, then yours to edit:", seeds.length > 12 ? [...seeds.slice(0, 10), `… and ${seeds.length - 10} more`] : seeds);
  const managed = steps.filter((s) => s.kind === "managed");
  const byTop = {};
  for (const s of managed) {
    const top = s.rel.split("/").slice(0, 2).join("/");
    byTop[top] = (byTop[top] || 0) + 1;
  }
  group("Harness files (replaced on update):", Object.entries(byTop).map(([k, n]) => `${k}  (${n} file${n > 1 ? "s" : ""})`));
  const edited = [...managed.filter((s) => s.edited), ...steps.filter((s) => s.kind === "remove" && s.edited)];
  group(force ? "Edited locally, will be overwritten (--force):" : "Edited locally, will be kept (use --force to replace):", edited.map((s) => s.rel));
  group("Remove (no longer part of the harness):", steps.filter((s) => s.kind === "remove" && (!s.edited || force)).map((s) => s.rel));
  group("Run:", steps.filter((s) => s.kind === "run").map((s) => s.cmd.join(" ")));
  return lines.join("\n");
}

function apply(ws, steps, managed, opts, log) {
  const recorded = readManifest(ws)?.files || {};
  const files = {};
  for (const s of steps) {
    const full = path.join(ws, s.rel || "");
    if (s.kind === "managed" && s.edited && !opts.force) { files[s.rel] = recorded[s.rel]; continue; }
    if (s.kind === "remove") {
      if (!s.edited || opts.force) fs.rmSync(full, { force: true });
      else files[s.rel] = recorded[s.rel]; // kept: still tracked, so a later --force can remove it
      continue;
    }
    if (s.kind === "run") {
      if (opts.noRun) { log(`  Run this yourself: ${s.cmd.join(" ")}`); continue; }
      if (!which(s.cmd[0])) { log(`  ! ${s.cmd[0]} not found; run this yourself: ${s.cmd.join(" ")}`); continue; }
      const r = spawnSync(s.cmd[0], s.cmd.slice(1), { cwd: ws, stdio: "inherit" });
      if (r.status !== 0) log(`  ! "${s.cmd.join(" ")}" failed; run it yourself once the problem is fixed`);
      continue;
    }
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, s.data);
  }
  for (const [rel, data] of managed) if (!(rel in files)) files[rel] = sha(data);
  const manifest = {
    name: PKG.name, version: PKG.version, installedAt: new Date().toISOString(),
    tools: opts.tools, claude: opts.tools.includes("claude-code") ? opts.claudeMode : null, files,
  };
  fs.mkdirSync(path.join(ws, ".pm-harness"), { recursive: true });
  fs.writeFileSync(path.join(ws, ".pm-harness/install.json"), JSON.stringify(manifest, null, 2) + "\n");
}

// ------------------------------------------------------------------ commands

async function ask(rl, question, fallback) {
  if (!rl) return fallback;
  const a = (await rl.question(question)).trim();
  return a || fallback;
}

function parseTools(value) {
  const ids = value.split(/[\s,]+/).filter(Boolean).map((v) => (/^\d+$/.test(v) ? TOOLS[Number(v) - 1]?.id : v));
  const bad = ids.filter((id) => !TOOLS.some((t) => t.id === id));
  if (bad.length || !ids.length) throw new Error(`unknown tool: ${bad.join(", ") || value}. Choose from ${TOOLS.map((t) => t.id).join(", ")}`);
  return [...new Set(ids)];
}

async function init(args, out) {
  const interactive = process.stdin.isTTY && !args.yes;
  const rl = interactive ? readline.createInterface({ input: process.stdin, output: process.stdout }) : null;
  try {
    out(`PM Harness ${PKG.version}: idea → PRD → behaviour trees → prototype → tickets, in any AI tool.\n`);
    const ws = path.resolve(args.dir || (await ask(rl, `Workspace folder [${process.cwd()}]: `, process.cwd())));
    let tools = args.tools ? parseTools(args.tools) : null;
    if (!tools) {
      if (rl) out(TOOLS.map((t, i) => `  ${i + 1}. ${t.label}`).join("\n"));
      tools = parseTools(await ask(rl, "Which AI tools do you use? Numbers, comma-separated [1]: ", "1"));
    }
    let claudeMode = args.claude || "plugin";
    if (tools.includes("claude-code") && !args.claude && rl) {
      out("Claude Code can use PM Harness as a plugin (recommended: updates itself, adds the\nsession-start board) or as project files in .claude/ (no plugin needed).");
      claudeMode = (await ask(rl, "  1. Plugin  2. Project files [1]: ", "1")) === "2" ? "files" : "plugin";
    }
    if (!["plugin", "files"].includes(claudeMode)) throw new Error("--claude must be plugin or files");
    const opts = { tools, claudeMode, force: !!args.force, noRun: !!args["no-plugin-install"] };
    const { steps, managed } = plan(ws, opts);
    out(`\nPlan for ${ws}:\n${describe(steps, opts.force) || "  Nothing to do."}\n`);
    if (args["dry-run"]) { out("Dry run: nothing written."); return 0; }
    if (rl && !/^y(es)?$/i.test(await ask(rl, "Go ahead? [y/N] ", "n"))) { out("Stopped. Nothing written."); return 1; }
    fs.mkdirSync(ws, { recursive: true });
    apply(ws, steps, managed, opts, out);
    out(`\nInstalled PM Harness ${PKG.version} in ${ws}.`);
    const py = python();
    if (!py?.ok) out("! Python 3.8+ was not found. The checks need it: install Python 3, then run doctor.");
    out("\nNext: open the folder in your AI tool and run the setup skill to map your connectors and fill in your context:");
    for (const id of tools) {
      const label = TOOLS.find((t) => t.id === id).label;
      const how = id === "claude-code" ? (claudeMode === "plugin" ? "/pm-harness:setup" : "/setup")
        : id === "codex" ? "$setup" : 'ask: "use the setup skill"';
      out(`  ${label}: ${how}`);
    }
    if (tools.includes("claude-code") && claudeMode === "files" && tools.some((t) => ["cursor", "copilot"].includes(t))) {
      out("  Note: Cursor and Copilot read both .claude/skills and .agents/skills, so they list each skill twice.");
    }
    return 0;
  } finally {
    rl?.close();
  }
}

async function update(args, out) {
  const ws = path.resolve(args.dir || process.cwd());
  const manifest = readManifest(ws);
  if (!manifest) { out(`No PM Harness installation in ${ws} (no .pm-harness/install.json). Run init first.`); return 1; }
  const opts = { tools: manifest.tools, claudeMode: manifest.claude || "plugin", force: !!args.force };
  const { steps, managed } = plan(ws, opts);
  const changes = steps.filter((s) => s.kind !== "run");
  out(`PM Harness ${manifest.version} → ${PKG.version} in ${ws}\n${describe(changes, opts.force) || "  Already up to date."}`);
  if (args["dry-run"]) { out("Dry run: nothing written."); return 0; }
  apply(ws, changes, managed, opts, out);
  if (opts.tools.includes("claude-code") && opts.claudeMode === "plugin") {
    out("\nClaude Code plugin: run `claude plugin marketplace update pm-harness` and `claude plugin update pm-harness@pm-harness`.");
  }
  out("Updated.");
  return 0;
}

function doctor(args, out) {
  const ws = path.resolve(args.dir || process.cwd());
  let problems = 0;
  const ok = (m) => out(`  ✓ ${m}`);
  const bad = (m) => { problems++; out(`  ✗ ${m}`); };
  const warn = (m) => out(`  ! ${m}`);
  out(`PM Harness doctor: ${ws}`);
  const manifest = readManifest(ws);
  if (!manifest) bad("no .pm-harness/install.json (run init)");
  else {
    ok(`installed version ${manifest.version} for ${manifest.tools.join(", ")}${manifest.claude ? ` (Claude Code: ${manifest.claude})` : ""}`);
    if (manifest.version !== PKG.version) warn(`version ${PKG.version} is available: run update`);
    let missing = 0, edited = 0;
    for (const [rel, hash] of Object.entries(manifest.files)) {
      const full = path.join(ws, rel);
      if (!exists(full)) missing++;
      else if (sha(fs.readFileSync(full)) !== hash) edited++;
    }
    if (missing) bad(`${missing} harness file(s) missing: run update`); else ok(`${Object.keys(manifest.files).length} harness files present`);
    if (edited) warn(`${edited} harness file(s) edited locally; update keeps them unless --force`);
    const broken = [];
    for (const rel of Object.keys(manifest.files).filter((r) => r.endsWith("SKILL.md"))) {
      const full = path.join(ws, rel);
      if (!exists(full)) continue;
      for (const m of readText(full).matchAll(/\.\.\/\.\.\/\.\.\/(\.pm-harness\/[\w./*-]+)/g)) {
        const target = m[1].replace(/\/\*.*$/, "").replace(/\.$/, "");
        if (target.includes("..") || !exists(path.join(ws, target))) broken.push(`${rel} → ${target}`);
      }
    }
    if (broken.length) bad(`skills refer to missing files: ${broken.slice(0, 3).join("; ")}`); else ok("skill references resolve");
  }
  for (const name of ["AGENTS.md", "CLAUDE.md"]) {
    const p = path.join(ws, name);
    if (!exists(p)) continue;
    const t = readText(p);
    if (name === "AGENTS.md") {
      if (!t.includes(MARKER)) bad("AGENTS.md has no workspace marker");
      else if (!t.includes(BEGIN)) bad("AGENTS.md has no PM Harness block: run update");
      else ok("AGENTS.md routes every tool");
    } else if (!/@AGENTS\.md/.test(t)) warn("CLAUDE.md does not import AGENTS.md");
  }
  const py = python();
  if (!py) bad("Python 3 not found: the checks need it");
  else if (!py.ok) bad(`Python ${py.version} found; the checks need 3.8+`);
  else {
    ok(`${py.cmd} ${py.version}`);
    const checker = path.join(ws, ".pm-harness/pm_check.py");
    if (exists(checker)) {
      const r = spawnSync(py.cmd, [checker, "workspace", ws], { encoding: "utf8" });
      out(r.stdout.trimEnd().split("\n").map((l) => "    " + l).join("\n"));
      if (r.status !== 0) bad("workspace check failed (see above)");
    }
  }
  if (manifest?.claude === "plugin") {
    if (!which("claude")) warn("Claude Code CLI not found; check the plugin is installed: /plugin in Claude Code");
    else {
      const r = spawnSync("claude", ["plugin", "list"], { encoding: "utf8" });
      if (r.status === 0 && r.stdout.includes("pm-harness")) ok("Claude Code plugin installed");
      else warn(`Claude Code plugin not found: claude plugin install ${PLUGIN_ID}`);
    }
  }
  out(problems ? `\n${problems} problem(s) found.` : "\nAll good.");
  return problems ? 1 : 0;
}

const HELP = `PM Harness ${PKG.version}

Usage: npx github:${MARKETPLACE} <command> [options]

Commands:
  init      install PM Harness into a workspace folder (asks which AI tools you use)
  update    replace the harness files with this version; your context and work are untouched
  doctor    check an installation

Options:
  --dir <path>       workspace folder (default: the current folder)
  --tools <list>     comma-separated: ${TOOLS.map((t) => t.id).join(", ")}
  --claude <mode>    plugin (default) or files: how Claude Code gets the skills
  --yes              do not ask; use the defaults and the options given
  --dry-run          show the plan, write nothing
  --force            replace harness files even if you edited them
  --no-plugin-install  print the Claude Code plugin commands instead of running them
  --version          print the version`;

export function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) { args._.push(a); continue; }
    const [k, v] = a.slice(2).split("=");
    if (["yes", "dry-run", "force", "help", "version", "no-plugin-install"].includes(k)) args[k] = true;
    else args[k] = v ?? argv[++i];
  }
  return args;
}

export async function main(argv, out = console.log) {
  const args = parseArgs(argv);
  if (args.version) { out(PKG.version); return 0; }
  const cmd = args._[0];
  if (!cmd || args.help) { out(HELP); return cmd ? 0 : 2; }
  try {
    if (cmd === "init") return await init(args, out);
    if (cmd === "update") return await update(args, out);
    if (cmd === "doctor") return doctor(args, out);
  } catch (err) {
    out(`Error: ${err.message}`);
    return 2;
  }
  out(`Unknown command: ${cmd}\n\n${HELP}`);
  return 2;
}

if (process.argv[1] && fs.realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).then((code) => process.exit(code));
}
