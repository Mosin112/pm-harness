#!/usr/bin/env python3
"""PM Harness checker: the verification gates behind the pipeline.

Usage:
  pm_check.py prd <prd.md> [trees-dir]                   PRD structure, phase rules, links to trees
  pm_check.py trees <trees-dir>                          grammar + testability of behaviour trees
  pm_check.py prototype <trees-dir> <prototype.html>     variants, tree coverage, review amendments
  pm_check.py tickets <trees-dir> <tickets.md>           tickets trace to trees, Definition of done
  pm_check.py workspace <workspace-dir>                  workspace layout and item stages
  pm_check.py board <workspace-dir>                      pipeline board for the start of a session
  pm_check.py plugin <plugin-dir>                        skills, agents, manifests and installer

Exit code 0 = pass (warnings allowed), 1 = errors found, 2 = usage problem.
Standard library only, Python 3.8+.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

KEYWORDS = ("when", "while", "if", "then", "and")
LEAF_WORDS = ("then", "and")
KINDS = ("Functional", "Journey", "Integration", "Unit")
COVERAGE_ORDER = ("src", "functional", "journey", "integration", "unit")
VAGUE = ("should", "properly", "correctly", "appropriately", "fast", "quickly", "easily",
         "user-friendly", "intuitive", "seamless", "etc", "and so on", "as needed")
STAGES = ("idea", "prd", "trees", "prototype", "tickets", "building", "launched", "parked")
LEGACY_STAGES = {"concept": "prd"}
PHASES = ("MVP", "MMP", "MLP", "Enhancement")
PRD_STATUSES = ("draft", "in review", "approved")
WORD_BUDGET = {"MVP": 1200, "MMP": 1800, "MLP": 1800, "Enhancement": 900}
AMENDMENT_STATUSES = ("open", "resolved", "dismissed")
AMENDMENT_CLASSES = ("prd change", "tree change", "polish", "later", "dismiss")
MARKER = "pm-harness-workspace"
FILE_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)_TEST_TREES\.md$")
HEAD_RE = re.compile(r"^(\w+): ([a-z0-9]+(?:-[a-z0-9]+)*) \((.+)\)$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    lines = [ln.rstrip("\n") for ln in read(path).splitlines()]
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


# ---------------------------------------------------------------- prd

SECTION_RE = re.compile(r"^## (\d+)\.?\s+(.+?)\s*$")
SUBSECTION_RE = re.compile(r"^### (\d+)\.(\d+)\.?\s+(.+?)\s*$")
PRIORITY_RE = re.compile(r"\((P[0-9])\)\s*$")
TREE_REF_RE = re.compile(r"^\s*(?:[-*]\s+)?\**Tree:?\**:?\s*`?(functional|journey)/([a-z0-9]+(?:-[a-z0-9]+)*)`?")


def strip_code(lines: list[str]) -> list[str]:
    out, fenced = [], False
    for ln in lines:
        if ln.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(ln)
    return out


def parse_prd(path: Path, report: Report) -> dict:
    lines = read(path).splitlines()
    prd = {"phase": None, "status": None, "sections": {}, "order": [], "capabilities": [],
           "journeys": [], "words": 0}

    header = next((ln for ln in lines[:12] if re.search(r"\bPhase\s*:", ln)), None)
    if header is None:
        report.error("no header line with 'Phase: …' under the title (see reference/prd-guide.md)")
    else:
        fields = {}
        for part in re.split(r"\s+·\s+|\s+\|\s+", header):
            if ":" in part:
                k, v = part.split(":", 1)
                fields[k.strip().strip("*").lower()] = v.strip().strip("*").strip()
        phase = fields.get("phase", "")
        match = next((p for p in PHASES if p.lower() == phase.lower()), None)
        if not match:
            report.error(f"phase '{phase}' must be one of {', '.join(PHASES)}")
        prd["phase"] = match
        status = fields.get("status")
        if status is None:
            report.warn("header has no 'Status:' (draft, in review or approved)")
        elif status.lower() not in PRD_STATUSES:
            report.error(f"status '{status}' must be one of {', '.join(PRD_STATUSES)}")
        prd["status"] = (status or "").lower()

    current = None
    sub = None
    for raw in strip_code(lines):
        sm = SECTION_RE.match(raw)
        if sm:
            current = int(sm.group(1))
            prd["order"].append(current)
            prd["sections"][current] = {"title": sm.group(2), "lines": []}
            sub = None
            continue
        if current is None:
            continue
        prd["sections"][current]["lines"].append(raw)
        ss = SUBSECTION_RE.match(raw)
        if ss:
            sub = (int(ss.group(1)), int(ss.group(2)), ss.group(3))
            if current == 5 and sub[0] == 5:
                pm = PRIORITY_RE.search(sub[2])
                prd["capabilities"].append({"num": f"5.{sub[1]}", "title": sub[2],
                                            "priority": pm.group(1) if pm else None, "trees": []})
            continue
        tm = TREE_REF_RE.match(raw)
        if tm:
            ref = f"{tm.group(1)}/{tm.group(2)}"
            if current == 5 and prd["capabilities"] and sub and sub[0] == 5:
                prd["capabilities"][-1]["trees"].append(ref)
            elif current == 5:
                report.error(f"§5: '{ref}' must sit inside a numbered capability (### 5.N)")
            if tm.group(1) == "journey":
                prd["journeys"].append(ref)
            elif current != 5:
                report.warn(f"§{current}: functional tree '{ref}' is named outside §5 Requirements")
        prd["words"] += len(re.findall(r"[A-Za-z0-9][\w'’-]*", raw))
    return prd


def section_text(prd: dict, num: int) -> str:
    return "\n".join(prd["sections"].get(num, {}).get("lines", []))


def check_prd_structure(prd: dict, report: Report) -> None:
    nums = prd["order"]
    for n in range(1, 9):
        if n not in prd["sections"]:
            report.error(f"missing section '## {n}. …' (the PRD has eight fixed sections)")
    extra = [n for n in nums if n < 1 or n > 8]
    for n in extra:
        report.error(f"§{n}: a PRD has eight sections; fold this into the closest one")
    core = [n for n in nums if 1 <= n <= 8]
    if core != sorted(core) or len(core) != len(set(core)):
        report.error(f"sections must appear once each, in order 1–8 (found {core})")
    for n in range(1, 9):
        body = [ln for ln in prd["sections"].get(n, {}).get("lines", []) if ln.strip()]
        if n in prd["sections"] and not [ln for ln in body if not ln.startswith("#")]:
            report.error(f"§{n} {prd['sections'][n]['title']}: section is empty")

    caps = prd["capabilities"]
    if 5 in prd["sections"] and not caps:
        report.error("§5 Requirements: add one '### 5.N <Capability> (P0)' subsection per capability")
    seen: dict[str, str] = {}
    for c in caps:
        if not c["priority"]:
            report.error(f"§{c['num']} {c['title']}: heading must end with a priority, e.g. (P0)")
        elif c["priority"] not in ("P0", "P1", "P2"):
            report.error(f"§{c['num']}: priority {c['priority']} must be P0, P1 or P2")
        functional = [t for t in c["trees"] if t.startswith("functional/")]
        if not functional:
            report.error(f"§{c['num']} {c['title']}: name its tree with 'Tree: functional/<subject>'")
        for t in c["trees"]:
            if t.startswith("journey/"):
                report.warn(f"§{c['num']}: journey trees belong in §6.1, not under a capability")
        for t in functional:
            if t in seen:
                report.error(f"§{c['num']}: '{t}' is already the tree for §{seen[t]} (one capability, one tree)")
            seen[t] = c["num"]

    phase = prd["phase"]
    s5, s6, s7 = section_text(prd, 5).lower(), section_text(prd, 6).lower(), section_text(prd, 7).lower()
    if phase == "MVP" and any(c["priority"] == "P2" for c in caps):
        report.warn("MVP: move P2 capabilities to §4 Later")
    if phase == "Enhancement" and "must not regress" not in s5:
        report.error("Enhancement: §5 needs a 'Must not regress' list (see reference/phases.md)")
    if phase in ("MMP", "MLP") and "launch gate" not in s7:
        report.error(f"{phase}: §7 needs a launch gate for each rollout stage")
    if phase == "MVP" and "gate" not in s7:
        report.warn("MVP: §7 should state the continue / stop gate")
    if phase == "MLP" and "polish" not in s5 + s6:
        report.warn("MLP: add polish criteria to §5 or §6")
    if 6 in prd["sections"] and not prd["journeys"]:
        report.warn("§6.1: end the core journey with 'Tree: journey/<subject>'")
    if 6 in prd["sections"] and "prototype decision" not in s6 and phase != "Enhancement":
        report.warn("§6.3: state the prototype decision the variants will argue about")

    in_questions = False  # inside a table whose first column is "Question"
    for ln in prd["sections"].get(8, {}).get("lines", []):
        if not ln.strip().startswith("|"):
            in_questions = False
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0].lower() == "question":
            in_questions = True
            continue
        if in_questions and len(cells) >= 2 and not set(cells[0]) <= set("-: "):
            if cells[1].lower() in ("", "?", "tbd", "none", "-"):
                report.warn(f"§8: open question has no owner: '{cells[0]}'")

    if phase:
        budget = WORD_BUDGET[phase]
        if prd["words"] > budget:
            report.warn(f"{prd['words']} words is over the {phase} guide of ~{budget}; cut what "
                        "does not change a decision")


def cmd_prd(prd_path: str, trees_dir: str | None = None) -> int:
    report = Report(f"PRD {prd_path}")
    path = Path(prd_path)
    if not path.is_file():
        report.error(f"PRD not found: {prd_path}")
        return report.finish()
    prd = parse_prd(path, report)
    check_prd_structure(prd, report)
    caps = prd["capabilities"]
    report.note(f"phase {prd['phase'] or '?'}, status {prd['status'] or '?'}, {len(caps)} "
                f"capabilities ({', '.join(c['priority'] or '?' for c in caps)}), ~{prd['words']} words")

    if trees_dir:
        trees = load_trees(Path(trees_dir), Report("(tree parse)"))
        have = {t["key"] for t in trees}
        named = {t for c in caps for t in c["trees"]} | set(prd["journeys"])
        for ref in sorted(named - have):
            report.error(f"PRD names tree '{ref}' but {trees_dir} has no such tree")
        for key in sorted(have - named):
            if key.startswith("functional/"):
                report.error(f"tree '{key}' is not named by any capability in §5 (add it or remove the tree)")
            elif key.startswith("journey/"):
                report.warn(f"tree '{key}' is not named in §6.1")
        report.note(f"{len(named & have)} of {len(named)} named trees found")
    return report.finish()


# ---------------------------------------------------------------- prototype

SCREEN_TAG_RE = re.compile(r"<[a-zA-Z][\w-]*\s[^<>]*?\bdata-screen=\"([^\"]+)\"[^<>]*>")
VARIANT_ATTR_RE = re.compile(r"\sdata-variant=\"([^\"]+)\"")


def json_block(html: str, block_id: str):
    m = re.search(rf'<script[^>]*id="{block_id}"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None, None
    try:
        return json.loads(m.group(1)), None
    except ValueError as exc:
        return None, str(exc)


def prototype_screens(html: str) -> tuple[set[str], dict[str, set[str]]]:
    shared: set[str] = set()
    by_variant: dict[str, set[str]] = {}
    for m in SCREEN_TAG_RE.finditer(html):
        vm = VARIANT_ATTR_RE.search(m.group(0))
        if vm:
            by_variant.setdefault(vm.group(1), set()).add(m.group(1))
        else:
            shared.add(m.group(1))
    return shared, by_variant


def check_variants(html: str, report: Report) -> list[str | None]:
    """Validate the variants manifest. Returns the variant ids (or [None] for one design)."""
    manifest, err = json_block(html, "prototype-variants")
    _, by_variant = prototype_screens(html)
    if err:
        report.error(f"prototype-variants block is not valid JSON: {err}")
        return [None]
    if manifest is None:
        if by_variant:
            report.error("screens use data-variant but there is no "
                         '<script type="application/json" id="prototype-variants"> block')
        else:
            report.warn("one design only: build-prototype expects 2 hypothesis-led variants "
                        "(one is fine for an Enhancement; declare it in a prototype-variants block)")
        return list(by_variant) or [None]

    if not str(manifest.get("decision", "")).strip():
        report.error("prototype-variants: 'decision' must state the trade-off the variants argue about")
    variants = manifest.get("variants")
    if not isinstance(variants, list) or not variants:
        report.error("prototype-variants: 'variants' must be a non-empty list")
        return list(by_variant) or [None]
    if len(variants) > 3:
        report.warn(f"{len(variants)} variants: more than three rarely sharpens a decision")
    if len(variants) == 1 and not str(manifest.get("singleReason", "")).strip():
        report.error("one variant needs a 'singleReason' (for example: an Enhancement compared with today)")
    ids: list[str] = []
    for i, v in enumerate(variants, 1):
        if not isinstance(v, dict):
            report.error(f"prototype-variants: variant {i} must be an object")
            continue
        vid = str(v.get("id", ""))
        if not KEBAB_RE.match(vid):
            report.error(f"prototype-variants: variant {i} id '{vid}' must be kebab-case")
        if vid in ids:
            report.error(f"prototype-variants: duplicate variant id '{vid}'")
        ids.append(vid)
        for field in ("label", "hypothesis"):
            if not str(v.get(field, "")).strip():
                report.error(f"variant '{vid}': '{field}' is empty")
        trade = v.get("tradeOffs")
        if not isinstance(trade, list) or not [t for t in trade if str(t).strip()]:
            report.error(f"variant '{vid}': 'tradeOffs' must list at least one trade-off")
    for vid in by_variant:
        if vid not in ids:
            report.error(f"data-variant '{vid}' is not declared in prototype-variants")
    if len(ids) > 1:
        for vid in ids:
            if vid not in by_variant:
                report.warn(f"variant '{vid}' has no screens of its own; it differs only in styling")
    report.note(f"{len(ids)} variant(s): {', '.join(ids)}")
    return ids


def parse_amendments(path: Path) -> list[dict]:
    items: list[dict] = []
    for ln in read(path).splitlines():
        hm = re.match(r"^##\s+(A\d+)\s*[·:-]\s*(.+?)\s*$", ln)
        if hm:
            items.append({"id": hm.group(1), "title": hm.group(2)})
            continue
        fm = re.match(r"^\s*-\s+\**([A-Za-z ]+?)\**:\s*(.*?)\s*$", ln)
        if fm and items:
            items[-1][fm.group(1).strip().lower()] = fm.group(2).strip().strip("`").strip()
    return items


def check_amendments(path: Path, variants: list, shared: set, by_variant: dict,
                     tree_lines: set, report: Report) -> None:
    items = parse_amendments(path)
    named_variants = [v for v in variants if v]
    counts = {s: 0 for s in AMENDMENT_STATUSES}
    seen: set[str] = set()
    for a in items:
        aid = a["id"]
        if aid in seen:
            report.error(f"amendments: duplicate id {aid}")
        seen.add(aid)
        status = a.get("status", "").lower()
        if status not in AMENDMENT_STATUSES:
            report.error(f"{aid}: status '{status}' must be one of {', '.join(AMENDMENT_STATUSES)}")
            continue
        counts[status] += 1
        if not a.get("note"):
            report.error(f"{aid}: 'Note' is empty")
        variant = a.get("variant") or None
        if len(named_variants) > 1 and not variant:
            report.error(f"{aid}: say which variant (one of {', '.join(named_variants)})")
        if variant and named_variants and variant not in named_variants:
            report.error(f"{aid}: variant '{variant}' is not declared")
        screen = a.get("screen")
        if not screen:
            report.error(f"{aid}: 'Screen' is empty")
        else:
            available = set(shared) | (by_variant.get(variant, set()) if variant else
                                       set().union(*by_variant.values()) if by_variant else set())
            if screen not in available:
                report.error(f"{aid}: screen '{screen}' does not exist"
                             + (f" in variant '{variant}'" if variant else ""))
        line = a.get("tree line")
        if line and tree_lines and line.strip('"') not in tree_lines and line not in tree_lines:
            report.error(f"{aid}: tree line is not in any tree: '{line}'")
        cls = a.get("class", "").lower()
        if status != "open":
            if cls not in AMENDMENT_CLASSES:
                report.error(f"{aid}: class '{cls}' must be one of {', '.join(AMENDMENT_CLASSES)}")
            if not a.get("resolution"):
                report.error(f"{aid}: a {status} amendment needs a 'Resolution'")
            if (status == "dismissed") != (cls == "dismiss"):
                report.error(f"{aid}: use status 'dismissed' with class 'dismiss', and only then")
    report.note(f"amendments: {counts['resolved']} resolved, {counts['dismissed']} dismissed, "
                f"{counts['open']} open")
    if counts["open"]:
        report.error(f"{counts['open']} open amendment(s): run review-prototype; the prototype "
                     "cannot be approved while any is open")


def cmd_prototype(trees_dir: str, html_path: str) -> int:
    report = Report(f"prototype {html_path}")
    trees = load_trees(Path(trees_dir), Report("(tree parse)"))
    html_file = Path(html_path)
    if not html_file.is_file():
        report.error(f"prototype not found: {html_path}")
        return report.finish()
    html = read(html_file)
    variants = check_variants(html, report)
    shared, by_variant = prototype_screens(html)
    all_screens = (shared | set().union(*by_variant.values())) if by_variant else set(shared)

    def screens_for(v: str | None) -> set[str]:
        return (shared | by_variant.get(v, set())) if v else all_screens

    report.note(f"{len(all_screens)} screens ({len(shared)} shared"
                + "".join(f", {len(s)} only in {v}" for v, s in sorted(by_variant.items())) + ")")

    cov, err = json_block(html, "tree-coverage")
    if err:
        report.error(f"coverage map is not valid JSON: {err}")
        return report.finish()
    if cov is None or not isinstance(cov.get("trees"), dict):
        report.error('no <script type="application/json" id="tree-coverage"> block with a "trees" object')
        return report.finish()
    cov = cov["trees"]

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
                covered += 1
                continue
            missing = [v for v in variants if screen not in screens_for(v)]
            if missing and variants == [None]:
                report.error(f"{t['key']}: '{leaf}' points at missing screen '{screen}'")
                continue
            if missing:
                report.error(f"{t['key']}: '{leaf}' needs screen '{screen}' in variant(s) "
                             f"{', '.join(missing)}; every variant must demonstrate every outcome")
                continue
            covered += 1
    for key in cov:
        if key not in {t["key"] for t in trees}:
            report.warn(f"coverage map mentions unknown tree '{key}'")
    report.note(f"{covered}/{total} tree outcomes demonstrated or justified in every variant")

    amend = html_file.parent / "amendments.md"
    if amend.is_file():
        tree_lines = {ln for t in trees for ln in t["lines"]}
        check_amendments(amend, variants, shared, by_variant, tree_lines, report)
    return report.finish()


# ---------------------------------------------------------------- tickets

def dod_blocks(lines: list[str]) -> list[int]:
    """Count checklist items under each 'Definition of done' heading or bold label."""
    blocks: list[int] = []
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if re.match(r"^(#+\s*|\*\*)definition of done", ln, re.I):
            items = 0
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if nxt.startswith("#") or nxt.startswith("---") or (nxt.startswith("**") and items):
                    break
                if re.match(r"^[-*]\s+\[[ xX]\]\s+\S", nxt):
                    items += 1
                j += 1
            blocks.append(items)
            i = j
            continue
        i += 1
    return blocks


def cmd_tickets(trees_dir: str, tickets_path: str) -> int:
    report = Report(f"tickets {tickets_path}")
    trees = load_trees(Path(trees_dir), Report("(tree parse)"))
    path = Path(tickets_path)
    if not path.is_file():
        report.error(f"tickets file not found: {tickets_path}")
        return report.finish()
    raw_lines = read(path).splitlines()
    ticket_lines = [ln.strip() for ln in raw_lines]
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

    blocks = dod_blocks(raw_lines)
    if not blocks:
        report.error("no 'Definition of done': add the team checklist from "
                     "context/definition-of-done.md, for all stories or per story")
    elif max(blocks) < 3:
        report.error("the Definition of done needs at least three checklist items ('- [ ] …')")
    else:
        report.note(f"Definition of done: {len(blocks)} block(s), {sum(blocks)} items")
    return report.finish()


# ---------------------------------------------------------------- workspace

CONTEXT_FILES = ("company", "product", "strategy", "users", "metrics", "stakeholders",
                 "constraints", "tools", "glossary", "writing-style")
NEW_CONTEXT_FILES = ("definition-of-done",)
FOLDERS = ("context", "decisions", "signals", "work", "meetings", "updates")


def is_workspace(root: Path) -> bool:
    for name in ("AGENTS.md", "CLAUDE.md"):
        p = root / name
        if p.is_file() and MARKER in read(p):
            return True
    return False


def item_stage(idea: Path) -> str | None:
    m = re.search(r"^stage:\s*(\S+)", read(idea), re.M)
    return m.group(1) if m else None


def item_files(folder: Path) -> dict[str, Path]:
    prd = folder / "02-prd.md"
    if not prd.exists() and (folder / "02-concept.md").exists():
        prd = folder / "02-concept.md"
    review = folder / "02-prd-review.md"
    if not review.exists() and (folder / "02-concept-review.md").exists():
        review = folder / "02-concept-review.md"
    return {"prd": prd, "review": review, "trees": folder / "03-trees",
            "prototype": folder / "04-prototype" / "index.html",
            "amendments": folder / "04-prototype" / "amendments.md",
            "tickets": folder / "05-tickets.md"}


def cmd_workspace(ws: str) -> int:
    root = Path(ws)
    report = Report(f"workspace {root}")
    if not is_workspace(root):
        report.error(f"AGENTS.md or CLAUDE.md with the {MARKER} marker not found")
    for d in FOLDERS:
        if not (root / d).is_dir():
            report.error(f"missing folder: {d}/")
    for f in CONTEXT_FILES + NEW_CONTEXT_FILES:
        p = root / "context" / f"{f}.md"
        if not p.is_file():
            if f in NEW_CONTEXT_FILES:
                report.warn(f"missing context/{f}.md: run the setup skill in repair mode")
            else:
                report.error(f"missing context file: context/{f}.md")
        elif len(read(p).splitlines()) > 150:
            report.warn(f"context/{f}.md is over 150 lines; consider splitting it")
    for idea in sorted((root / "work").glob("*/01-idea.md")):
        item = idea.parent.name
        stage = item_stage(idea)
        if stage in LEGACY_STAGES:
            report.warn(f"work/{item}: stage '{stage}' is the old name for '{LEGACY_STAGES[stage]}'")
            stage = LEGACY_STAGES[stage]
        if stage not in STAGES:
            report.error(f"work/{item}: stage '{stage}' must be one of {', '.join(STAGES)}")
            continue
        report.note(f"work/{item}: {stage}")
        if stage == "parked":
            continue
        files = item_files(idea.parent)
        order = STAGES.index(stage)
        needs = {1: ("prd", "02-prd.md"), 2: ("trees", "03-trees/"),
                 3: ("prototype", "04-prototype/index.html"), 4: ("tickets", "05-tickets.md")}
        for level, (key, label) in needs.items():
            if order >= level and not files[key].exists():
                report.error(f"work/{item}: stage '{stage}' but {label} is missing")
    return report.finish()


# ---------------------------------------------------------------- board

NEXT_STEP = {
    "idea": "product-grill if the idea is fuzzy, then write-prd (opportunity-brief to size it first)",
    "prd": "write-behaviour-trees",
    "trees": "build-prototype",
    "prototype": "create-eng-tickets",
    "tickets": "stakeholder-update; launch-readout after launch",
    "building": "stakeholder-update; launch-readout after launch",
    "launched": "done or update-context to capture what was learned",
    "parked": "parked; see the decision log",
}


def open_blocking(review: Path) -> int:
    if not review.is_file():
        return 0
    n = 0
    for ln in read(review).splitlines():
        cells = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
        if len(cells) > 2 and "blocking" in cells[:3] and cells[-1] in ("open", "", "(filled in after revision)"):
            n += 1
    return n


def cmd_board(ws: str) -> int:
    root = Path(ws)
    if not is_workspace(root):
        return 0
    print("## PM Harness pipeline board")
    items = sorted((root / "work").glob("*/01-idea.md"))
    for idea in items:
        text = read(idea)
        stage = item_stage(idea) or "?"
        stage = LEGACY_STAGES.get(stage, stage)
        updated = (re.search(r"^updated:\s*(\S+)", text, re.M) or [None, "?"])[1]
        flags = []
        files = item_files(idea.parent)
        blocking = open_blocking(files["review"])
        if blocking:
            flags.append(f"{blocking} open blocking review finding(s)")
        if files["amendments"].is_file():
            open_a = sum(1 for a in parse_amendments(files["amendments"])
                         if a.get("status", "").lower() == "open")
            if open_a:
                flags.append(f"{open_a} open prototype amendment(s): review-prototype")
        phase = ""
        if files["prd"].is_file():
            pm = re.search(r"\bPhase\s*:\s*\**\s*([A-Za-z]+)", read(files["prd"]))
            phase = f" ({pm.group(1)})" if pm else ""
        line = f"- {idea.parent.name}{phase} | stage: {stage} | updated: {updated} | next: {NEXT_STEP.get(stage, 'check 01-idea.md')}"
        if flags:
            line += " | ⚠ " + "; ".join(flags)
        print(line)
    if not items:
        print("- No items yet. Start with capture-idea, synthesize-signals or desktop-research.")
    ctx = root / "context"
    if ctx.is_dir():
        cutoff = time.time() - 90 * 86400
        stale = sorted(str(p.relative_to(root)) for p in ctx.glob("*.md") if p.stat().st_mtime < cutoff)
        if stale:
            print("Context files not updated in 90+ days (offer to review them): " + " ".join(stale))
    print("Reminders: follow AGENTS.md and the evidence rules; never write to an external tool "
          "without the PM's approval; run done at the end of a useful session.")
    return 0


# ---------------------------------------------------------------- plugin

def frontmatter(path: Path) -> dict | None:
    text = read(path)
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
    versions = {}
    for manifest in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                     "hooks/hooks.json", "package.json"):
        p = root / manifest
        try:
            data = json.loads(read(p))
        except FileNotFoundError:
            report.error(f"missing {manifest}")
            continue
        except ValueError as exc:
            report.error(f"{manifest} is not valid JSON: {exc}")
            continue
        if manifest.endswith("plugin.json") or manifest == "package.json":
            versions[manifest] = data.get("version")
        if manifest.endswith("marketplace.json"):
            versions[manifest] = (data.get("plugins") or [{}])[0].get("version")
        if manifest == "package.json":
            for name, rel in (data.get("bin") or {}).items():
                if not (root / rel).is_file():
                    report.error(f"package.json bin '{name}' points at missing {rel}")
    if len(set(versions.values())) > 1:
        report.error("versions differ: " + ", ".join(f"{k}={v}" for k, v in versions.items()))
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        report.error("no skills found")
    names = {s.parent.name for s in skills}
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
        text = read(s)
        for ref in re.findall(r"\.\./\.\./([\w./-]+)", text):
            if not (root / ref.rstrip(".")).exists():
                report.error(f"skills/{name}: refers to missing file {ref}")
        for other in re.findall(r"/pm-harness:([a-z0-9-]+)", text):
            if other not in names:
                report.error(f"skills/{name}: refers to unknown skill /pm-harness:{other}")
        for other in re.findall(r"the `([a-z0-9-]+)` skill", text):
            if other not in names:
                report.error(f"skills/{name}: refers to unknown skill `{other}`")
    agents = sorted((root / "agents").glob("*.md"))
    for a in agents:
        fm = frontmatter(a)
        if not fm or not fm.get("name") or not fm.get("description"):
            report.error(f"agents/{a.name}: needs name and description frontmatter")
        elif fm["name"] != a.stem:
            report.error(f"agents/{a.name}: name '{fm['name']}' must equal file name")
    template = root / "templates" / "workspace"
    if template.is_dir() and not is_workspace(template):
        report.error(f"templates/workspace: AGENTS.md or CLAUDE.md needs the {MARKER} marker")
    report.note(f"{len(skills)} skills, {len(agents)} agents, version {next(iter(versions.values()), '?')}")
    return report.finish()


def main(argv: list[str]) -> int:
    commands = {
        "prd": (cmd_prd, (1, 2)),
        "trees": (cmd_trees, (1,)),
        "prototype": (cmd_prototype, (2,)),
        "tickets": (cmd_tickets, (2,)),
        "workspace": (cmd_workspace, (1,)),
        "board": (cmd_board, (1,)),
        "plugin": (cmd_plugin, (1,)),
    }
    if len(argv) < 2 or argv[1] not in commands or len(argv) - 2 not in commands[argv[1]][1]:
        print(__doc__)
        return 2
    fn, _ = commands[argv[1]]
    return fn(*argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
