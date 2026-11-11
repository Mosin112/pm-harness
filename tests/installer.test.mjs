// Installer tests: node --test tests/
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { main, rewriteSkill, withBlock } from "../cli/pm-harness.mjs";

const run = async (...argv) => {
  const lines = [];
  const code = await main(argv, (l) => lines.push(String(l)));
  return { code, out: lines.join("\n") };
};
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), "pmh-"));
const read = (...p) => fs.readFileSync(path.join(...p), "utf8");
const check = (ws) => spawnSync("python3", [path.join(ws, ".pm-harness/pm_check.py"), "workspace", ws], { encoding: "utf8" });

test("rewrites plugin-relative paths for installed skills", () => {
  assert.equal(rewriteSkill("Read `../../reference/x.md`"), "Read `../../../.pm-harness/reference/x.md`");
  assert.equal(rewriteSkill("`../../scripts/pm_check.py`"), "`../../../.pm-harness/pm_check.py`");
});

test("init for Codex and Gemini: AGENTS.md, .agents/skills, no Claude files", async () => {
  const ws = tmp();
  const { code } = await run("init", "--dir", ws, "--tools", "codex,gemini", "--yes");
  assert.equal(code, 0);
  assert.ok(read(ws, "AGENTS.md").includes("pm-harness-workspace"));
  assert.ok(read(ws, "AGENTS.md").includes("<!-- pm-harness:begin -->"));
  assert.equal(read(ws, "GEMINI.md"), "@./AGENTS.md\n");
  assert.ok(fs.existsSync(path.join(ws, ".agents/skills/write-prd/SKILL.md")));
  assert.ok(!fs.existsSync(path.join(ws, "CLAUDE.md")));
  assert.ok(!fs.existsSync(path.join(ws, ".claude")));
  assert.ok(read(ws, ".agents/skills/write-prd/SKILL.md").includes("../../../.pm-harness/reference/prd-guide.md"));
  assert.equal(check(ws).status, 0, check(ws).stdout);
  const doc = await run("doctor", "--dir", ws);
  assert.equal(doc.code, 0, doc.out);
});

test("init for Claude Code as project files adds skills, agents and the board hook", async () => {
  const ws = tmp();
  const { code } = await run("init", "--dir", ws, "--tools", "claude-code", "--claude", "files", "--yes");
  assert.equal(code, 0);
  assert.ok(read(ws, "CLAUDE.md").includes("@AGENTS.md"));
  assert.ok(fs.existsSync(path.join(ws, ".claude/skills/one-shot/SKILL.md")));
  assert.ok(fs.existsSync(path.join(ws, ".claude/agents/risk-reviewer.md")));
  const settings = JSON.parse(read(ws, ".claude/settings.json"));
  assert.ok(JSON.stringify(settings.hooks.SessionStart).includes("pm_check.py"));
  assert.ok(settings.permissions.ask.length > 0, "keeps the approval rules");
  const again = await run("init", "--dir", ws, "--tools", "claude-code", "--claude", "files", "--yes");
  assert.match(again.out, /Nothing to do/);
});

test("update keeps the PM's files and local edits, --force replaces edits", async () => {
  const ws = tmp();
  await run("init", "--dir", ws, "--tools", "codex", "--yes");
  fs.writeFileSync(path.join(ws, "context/users.md"), "# Users\nMy notes\n");
  const skill = path.join(ws, ".agents/skills/done/SKILL.md");
  fs.appendFileSync(skill, "\nlocal tweak\n");
  fs.writeFileSync(path.join(ws, "AGENTS.md"), read(ws, "AGENTS.md").replace("<team / product area>", "Payments"));
  let r = await run("update", "--dir", ws);
  assert.equal(r.code, 0);
  assert.match(r.out, /Edited locally, will be kept/);
  assert.equal(read(ws, "context/users.md"), "# Users\nMy notes\n");
  assert.ok(read(skill).includes("local tweak"));
  assert.ok(read(ws, "AGENTS.md").includes("Payments"), "PM edits above the block survive");
  r = await run("update", "--dir", ws, "--force");
  assert.ok(!read(skill).includes("local tweak"));
});

test("update removes harness files that are no longer shipped", async () => {
  const ws = tmp();
  await run("init", "--dir", ws, "--tools", "codex", "--yes");
  const manifestPath = path.join(ws, ".pm-harness/install.json");
  const manifest = JSON.parse(read(manifestPath));
  const stale = ".agents/skills/old-skill/SKILL.md";
  fs.mkdirSync(path.join(ws, ".agents/skills/old-skill"), { recursive: true });
  fs.writeFileSync(path.join(ws, stale), "old");
  manifest.files[stale] = "c8d2b6f8dd1e5d2bd3e0fd5cf87f1b42c6dc1a4b4f5d3d0d3b6c8b0e8e9e0a1b"; // not its hash: edited
  fs.writeFileSync(manifestPath, JSON.stringify(manifest));
  let r = await run("update", "--dir", ws);
  assert.ok(fs.existsSync(path.join(ws, stale)), "an edited stale file is kept");
  r = await run("update", "--dir", ws, "--force");
  assert.ok(!fs.existsSync(path.join(ws, stale)));
  assert.equal(r.code, 0);
});

test("a 0.1 workspace moves its CLAUDE.md content into AGENTS.md", async () => {
  const ws = tmp();
  const old = "<!-- pm-harness-workspace -->\n# PM workspace\n\nProduct work for **Payments**.\n";
  fs.writeFileSync(path.join(ws, "CLAUDE.md"), old);
  await run("init", "--dir", ws, "--tools", "claude-code,cursor", "--claude", "plugin", "--yes", "--no-plugin-install");
  const agents = read(ws, "AGENTS.md");
  assert.ok(agents.includes("Product work for **Payments**."));
  assert.ok(agents.includes("<!-- pm-harness:begin -->"));
  assert.ok(read(ws, "CLAUDE.md").includes("@AGENTS.md"));
  assert.ok(!fs.existsSync(path.join(ws, ".claude/skills")), "plugin mode writes no Claude skills");
  assert.ok(fs.existsSync(path.join(ws, ".agents/skills/setup/SKILL.md")));
});

test("an unrelated AGENTS.md gets the workspace section appended, not replaced", () => {
  const out = withBlock("# My repo\nRun tests with make.\n");
  assert.ok(out.startsWith("# My repo\nRun tests with make.\n"));
  assert.ok(out.includes("<!-- pm-harness:end -->"));
});

test("dry run writes nothing; bad tools are refused", async () => {
  const ws = tmp();
  const r = await run("init", "--dir", ws, "--tools", "codex", "--yes", "--dry-run");
  assert.equal(r.code, 0);
  assert.deepEqual(fs.readdirSync(ws), []);
  const bad = await run("init", "--dir", ws, "--tools", "notepad", "--yes");
  assert.equal(bad.code, 2);
  assert.match(bad.out, /unknown tool/);
});
