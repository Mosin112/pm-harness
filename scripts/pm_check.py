#!/usr/bin/env python3
"""PM Harness checker: the verification gates behind the pipeline.

Usage:
  pm_check.py trees <trees-dir>                          grammar + testability of behaviour trees
  pm_check.py prototype <trees-dir> <prototype.html>     every tree outcome is demonstrable
  pm_check.py tickets <trees-dir> <tickets.md>           tickets trace to trees, both ways
  pm_check.py workspace <workspace-dir>                  workspace layout and item stages
  pm_check.py plugin <plugin-dir>                        skills, agents and manifests are valid

Exit code 0 = pass (warnings allowed), 1 = errors found, 2 = usage problem.
Standard library only, Python 3.8+.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KEYWORDS = ("when", "while", "if", "then", "and")
LEAF_WORDS = ("then", "and")
KINDS = ("Functional", "Journey", "Integration", "Unit")
COVERAGE_ORDER = ("src", "functional", "journey", "integration", "unit")
VAGUE = ("should", "properly", "correctly", "appropriately", "fast", "quickly", "easily",
         "user-friendly", "intuitive", "seamless", "etc", "and so on", "as needed")
STAGES = ("idea", "concept", "trees", "prototype", "tickets", "building", "launched", "parked")
FILE_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)_TEST_TREES\.md$")
HEAD_RE = re.compile(r"^(\w+): ([a-z0-9]+(?:-[a-z0-9]+)*) \((.+)\)$")


class Report:
    def __init__(self, title: str):
        self.title = title
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    def finish(self) -> int:
        status = "FAIL" if self.errors else "PASS"
        print(f"{status}  {self.title}")
        for n in self.notes:
            print(f"  · {n}")
        for e in self.errors:
            print(f"  ✗ {e}")
        for w in self.warnings:
            print(f"  ! {w}")
        print(f"  {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


# ---------------------------------------------------------------- trees

def tree_files(trees_dir: Path) -> list[Path]:
    return sorted(p for p in trees_dir.rglob("*.md") if p.is_file())


def parse_tree(path: Path, report: Report) -> dict | None:
    """Parse one tree file; record problems on the report. Returns the parsed tree."""
    rel = path.name
    m = FILE_RE.match(path.name)
    if not m:
        report.error(f"{rel}: file name must be <kebab-case-subject>_TEST_TREES.md")
        return None
    subject = m.group(1)
    lines = [ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines()]
    body = [(i + 1, ln) for i, ln in enumerate(lines) if ln.strip()]
    if not body:
        report.error(f"{rel}: file is empty")
        return None

    lineno, head = body[0]
    hm = HEAD_RE.match(head)
    if not hm:
        report.error(f"{rel}:{lineno}: first line must be '<Kind>: <subject> (<coverage>)'")
        return None
    kind, head_subject, coverage = hm.groups()
    if kind not in KINDS:
        report.error(f"{rel}:{lineno}: kind '{kind}' must be one of {', '.join(KINDS)}")
    if head_subject != subject:
        report.error(f"{rel}:{lineno}: subject '{head_subject}' must match file name '{subject}'")
    folder = path.parent.name.lower()
    if folder in ("functional", "journey", "integration", "unit") and folder != kind.lower():
        report.error(f"{rel}: a {kind} tree must not live in the '{folder}' folder")

    keys = []
    for part in coverage.split(";"):
        if ":" not in part:
            report.error(f"{rel}:{lineno}: coverage entry '{part.strip()}' must be 'label: value'")
            continue
        key, value = (s.strip() for s in part.split(":", 1))
        if key not in COVERAGE_ORDER:
            report.error(f"{rel}:{lineno}: unknown coverage label '{key}'")
        elif not value:
            report.error(f"{rel}:{lineno}: coverage label '{key}' has no value (use 'none')")
        keys.append(key)
    known = [k for k in keys if k in COVERAGE_ORDER]
    if known != sorted(known, key=COVERAGE_ORDER.index):
        report.error(f"{rel}:{lineno}: coverage labels must follow the order {', '.join(COVERAGE_ORDER)}")
    if kind.lower() in COVERAGE_ORDER and kind.lower() not in keys:
        report.warn(f"{rel}:{lineno}: coverage does not mention '{kind.lower()}'")

    nodes = []  # (lineno, depth, word, text)
    for lineno, ln in body[1:]:
        indent = len(ln) - len(ln.lstrip(" "))
        if "\t" in ln[: indent + 1]:
            report.error(f"{rel}:{lineno}: use spaces, not tabs")
            continue
        if indent % 2:
            report.error(f"{rel}:{lineno}: indentation must be a multiple of two spaces")
            continue
        text = ln.strip()
        word = text.split(" ", 1)[0]
        if word not in KEYWORDS:
            report.error(f"{rel}:{lineno}: line must start with one of {', '.join(KEYWORDS)}: '{text}'")
            continue
        if len(text.split()) < 3:
            report.error(f"{rel}:{lineno}: clause is too short to be meaningful: '{text}'")
        nodes.append((lineno, indent // 2, word, text))

    if not nodes:
        report.error(f"{rel}: tree has no requirement lines")
        return None

    prev_depth = 0
    for idx, (lineno, depth, word, text) in enumerate(nodes):
        if depth == 0:
            report.error(f"{rel}:{lineno}: requirement lines must be indented under the first line")
        if depth == 1 and word != "when":
            report.error(f"{rel}:{lineno}: top-level lines must start with 'when'")
        if depth > prev_depth + 1:
            report.error(f"{rel}:{lineno}: indented more than one level below the line above")
        if idx > 0:
            p_line, p_depth, p_word, _ = nodes[idx - 1]
            if depth > p_depth and p_word in LEAF_WORDS:
                report.error(f"{rel}:{lineno}: nothing may nest under a '{p_word}' line (line {p_line})")
        if word == "and":
            prior = nodes[idx - 1] if idx > 0 else None
            if not (prior and prior[1] == depth and prior[2] in LEAF_WORDS):
                report.error(f"{rel}:{lineno}: 'and' must directly follow a 'then' or 'and' at the same depth")
        if word in LEAF_WORDS:
            lowered = f" {text.lower()} "
            for vague in VAGUE:
                if re.search(rf"\b{re.escape(vague)}\b", lowered):
                    report.warn(f"{rel}:{lineno}: '{vague}' is hard to test; name the observable result")
        prev_depth = depth

    # every non-leaf must eventually reach a 'then'
    for idx, (lineno, depth, word, text) in enumerate(nodes):
        if word in LEAF_WORDS:
            continue
        has_then = False
        for later in nodes[idx + 1:]:
            if later[1] <= depth:
                break
            if later[2] == "then":
                has_then = True
                break
        if not has_then:
            report.error(f"{rel}:{lineno}: branch '{text}' never reaches a 'then' outcome")

    leaves = [text for (_, _, word, text) in nodes if word in LEAF_WORDS]
    return {"kind": kind, "subject": subject, "key": f"{kind.lower()}/{subject}",
            "leaves": leaves, "lines": [n[3] for n in nodes], "path": path}


def load_trees(trees_dir: Path, report: Report) -> list[dict]:
    if not trees_dir.is_dir():
        report.error(f"trees folder not found: {trees_dir}")
        return []
    files = tree_files(trees_dir)
    if not files:
        report.error(f"no tree files in {trees_dir}")
    trees = [t for t in (parse_tree(p, report) for p in files) if t]
    kinds = {t["kind"] for t in trees}
    if trees and "Journey" not in kinds:
        report.warn("no Journey tree: write one per job-to-be-done")
    if trees and "Functional" not in kinds:
        report.warn("no Functional tree: every user-visible behaviour needs Functional coverage")
    return trees


def cmd_trees(trees_dir: str) -> int:
    report = Report(f"behaviour trees in {trees_dir}")
    trees = load_trees(Path(trees_dir), report)
    for t in trees:
        report.note(f"{t['key']}: {len(t['lines'])} lines, {len(t['leaves'])} outcomes")
    return report.finish()


# ---------------------------------------------------------------- prototype

def cmd_prototype(trees_dir: str, html_path: str) -> int:
    report = Report(f"prototype coverage for {html_path}")
    trees = load_trees(Path(trees_dir), Report("(tree parse)"))
    html_file = Path(html_path)
    if not html_file.is_file():
        report.error(f"prototype not found: {html_path}")
        return report.finish()
    html = html_file.read_text(encoding="utf-8")
    m = re.search(r'<script[^>]*id="tree-coverage"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        report.error('no <script type="application/json" id="tree-coverage"> block')
        return report.finish()
    try:
        cov = json.loads(m.group(1))["trees"]
    except (ValueError, KeyError, TypeError) as exc:
        report.error(f"coverage map is not valid JSON with a 'trees' object: {exc}")
        return report.finish()
    screens = set(re.findall(r'data-screen="([^"]+)"', html))
    report.note(f"{len(screens)} screens found")

    total = covered = 0
    for t in trees:
        entries = cov.get(t["key"])
        if entries is None:
            report.error(f"{t['key']}: tree missing from coverage map")
            continue
        mapped = {}
        for e in entries:
            line = (e.get("line") or "").strip()
            mapped[line] = e
            if line not in t["leaves"]:
                report.error(f"{t['key']}: coverage line is not an outcome in the tree: '{line}'")
        for leaf in t["leaves"]:
            total += 1
            e = mapped.get(leaf)
            if not e:
                report.error(f"{t['key']}: outcome not demonstrated: '{leaf}'")
                continue
            screen = e.get("screen")
            if screen is None:
                if not (e.get("reason") or "").strip():
                    report.error(f"{t['key']}: '{leaf}' has no screen and no reason")
                    continue
            elif screen not in screens:
                report.error(f"{t['key']}: '{leaf}' points at missing screen '{screen}'")
                continue
            covered += 1
    for key in cov:
        if key not in {t["key"] for t in trees}:
            report.warn(f"coverage map mentions unknown tree '{key}'")
    report.note(f"{covered}/{total} tree outcomes demonstrated or justified")
    return report.finish()


# ---------------------------------------------------------------- tickets

def cmd_tickets(trees_dir: str, tickets_path: str) -> int:
    report = Report(f"ticket traceability for {tickets_path}")
    trees = load_trees(Path(trees_dir), Report("(tree parse)"))
    path = Path(tickets_path)
    if not path.is_file():
        report.error(f"tickets file not found: {tickets_path}")
        return report.finish()
    ticket_lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    ticket_outcomes = {ln for ln in ticket_lines if ln.split(" ", 1)[0] in LEAF_WORDS}
    all_tree_lines = {ln for t in trees for ln in t["lines"]}

    total = 0
    for t in trees:
        for leaf in t["leaves"]:
            total += 1
            if leaf not in ticket_outcomes:
                report.error(f"{t['key']}: outcome not in any ticket: '{leaf}'")
    for ln in sorted(ticket_outcomes - all_tree_lines):
        report.error(f"ticket requirement not found in any tree (invented or reworded): '{ln}'")
    report.note(f"{total} tree outcomes, {len(ticket_outcomes)} outcome lines in tickets")
    return report.finish()


# ---------------------------------------------------------------- workspace

def cmd_workspace(ws: str) -> int:
    root = Path(ws)
    report = Report(f"workspace {root}")
    claude = root / "CLAUDE.md"
    if not claude.is_file() or "pm-harness-workspace" not in claude.read_text(encoding="utf-8"):
        report.error("CLAUDE.md with the pm-harness-workspace marker not found")
    for d in ("context", "decisions", "signals", "work", "meetings", "updates"):
        if not (root / d).is_dir():
            report.error(f"missing folder: {d}/")
    for f in ("company", "product", "strategy", "users", "metrics", "stakeholders",
              "constraints", "tools", "glossary", "writing-style"):
        p = root / "context" / f"{f}.md"
        if not p.is_file():
            report.error(f"missing context file: context/{f}.md")
        elif len(p.read_text(encoding="utf-8").splitlines()) > 150:
            report.warn(f"context/{f}.md is over 150 lines; consider splitting it")
    for idea in sorted((root / "work").glob("*/01-idea.md")):
        text = idea.read_text(encoding="utf-8")
        m = re.search(r"^stage:\s*(\S+)", text, re.M)
        stage = m.group(1) if m else None
        item = idea.parent.name
        if stage not in STAGES:
            report.error(f"work/{item}: stage '{stage}' must be one of {', '.join(STAGES)}")
            continue
        report.note(f"work/{item}: {stage}")
        order = STAGES.index(stage)
        needs = {1: "02-concept.md", 2: "03-trees", 3: "04-prototype/index.html", 4: "05-tickets.md"}
        for level, rel in needs.items():
            if order >= level and stage != "parked" and not (idea.parent / rel).exists():
                report.error(f"work/{item}: stage '{stage}' but {rel} is missing")
    return report.finish()


# ---------------------------------------------------------------- plugin

def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data = {}
    for ln in m.group(1).splitlines():
        if ":" in ln and not ln.startswith(" "):
            k, v = ln.split(":", 1)
            data[k.strip()] = v.strip()
    return data


def cmd_plugin(plugin_dir: str) -> int:
    root = Path(plugin_dir)
    report = Report(f"plugin {root}")
    for manifest in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "hooks/hooks.json"):
        p = root / manifest
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except FileNotFoundError:
            report.error(f"missing {manifest}")
        except ValueError as exc:
            report.error(f"{manifest} is not valid JSON: {exc}")
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        report.error("no skills found")
    for s in skills:
        fm = frontmatter(s)
        name = s.parent.name
        if fm is None:
            report.error(f"skills/{name}: SKILL.md has no frontmatter")
            continue
        if fm.get("name") != name:
            report.error(f"skills/{name}: frontmatter name '{fm.get('name')}' must equal folder name")
        desc = fm.get("description", "")
        if not desc:
            report.error(f"skills/{name}: description is empty")
        elif len(desc) > 1024:
            report.error(f"skills/{name}: description is over 1024 characters")
        elif not desc.lower().startswith("use "):
            report.warn(f"skills/{name}: description should start with 'Use when…' so it triggers")
        for ref in re.findall(r"\.\./\.\./([\w./-]+)", s.read_text(encoding="utf-8")):
            if not (root / ref).exists():
                report.error(f"skills/{name}: refers to missing file {ref}")
    agents = sorted((root / "agents").glob("*.md"))
    for a in agents:
        fm = frontmatter(a)
        if not fm or not fm.get("name") or not fm.get("description"):
            report.error(f"agents/{a.name}: needs name and description frontmatter")
        elif fm["name"] != a.stem:
            report.error(f"agents/{a.name}: name '{fm['name']}' must equal file name")
    report.note(f"{len(skills)} skills, {len(agents)} agents")
    return report.finish()


def main(argv: list[str]) -> int:
    commands = {
        "trees": (cmd_trees, 1),
        "prototype": (cmd_prototype, 2),
        "tickets": (cmd_tickets, 2),
        "workspace": (cmd_workspace, 1),
        "plugin": (cmd_plugin, 1),
    }
    if len(argv) < 2 or argv[1] not in commands or len(argv) - 2 != commands[argv[1]][1]:
        print(__doc__)
        return 2
    fn, _ = commands[argv[1]]
    return fn(*argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
