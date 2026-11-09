#!/usr/bin/env python3
"""PM Harness checker: the verification gates behind the pipeline.

Usage:
  pm_check.py item <work/item>                           every check that applies to one item
  pm_check.py prd <prd.md> [trees-dir]                   PRD structure, phase rules, links to trees
  pm_check.py trees <trees-dir>                          grammar + testability of behaviour trees
  pm_check.py prototype <trees-dir> <prototype.html>     variants, tree coverage, review amendments
  pm_check.py tickets <trees-dir> <tickets.md> [prd.md]  tickets trace to trees, metrics, Definition of done
  pm_check.py workspace <workspace-dir>                  workspace layout and item stages
  pm_check.py design <DESIGN.md>                         design tokens, references and section order
  pm_check.py board <workspace-dir>                      pipeline board for the start of a session
  pm_check.py plugin <plugin-dir>                        skills, agents, manifests and installer
  pm_check.py needs <skill>... | all [--tools <tools.md>] what a skill needs and which tools serve it

Generators:
  pm_check.py view <work/item>                           03-trees-view.html: the trees as a diagram to review
  pm_check.py contracts <work/item>                      05-contracts/: trees as engineering-harness contracts
  pm_check.py artifact <page.html> <out.html>            a full HTML page as a Claude artifact fragment

Exit code 0 = pass (warnings allowed), 1 = errors found, 2 = usage problem.
Standard library only, Python 3.8+.
"""
from __future__ import annotations

import contextlib
import hashlib
import html.parser as html_parser
import io
import json
import os
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
RESERVED_HASHES = ("settings", "sidebar", "customize", "upgrade", "downloads")
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
            "leaves": leaves, "lines": [n[3] for n in nodes], "path": path,
            "nodes": nodes, "coverage": coverage}


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
SEAM_RE = re.compile(r"^\s*(?:[-*]\s+)?\**Seam:?\**:?\s*(.+?)\s*$")
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
           "journeys": [], "words": 0, "journey_seam": None, "links": {}}
    for ln in lines[:12]:
        if re.match(r"^\**Links\**\s*:", ln):
            for label, url in re.findall(r"([A-Za-z][\w ]*?)\s*:?\s*<?(https?://[^\s>·|]+)", ln.split(":", 1)[1]):
                prd["links"][label.strip().lower()] = url

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
        sm2 = SEAM_RE.match(raw)
        if sm2:
            if current == 5 and prd["capabilities"] and sub and sub[0] == 5:
                prd["capabilities"][-1]["seam"] = sm2.group(1).strip()
            elif current == 6:
                prd["journey_seam"] = sm2.group(1).strip()
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
        if not c.get("seam"):
            report.warn(f"§{c['num']} {c['title']}: add a 'Seam:' line (where engineering tests it)")
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
    if 2 in prd["sections"] and "market" not in section_text(prd, 2).lower():
        report.warn("§2: add a 'Markets and languages' row")
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

SCREEN_TAG_RE = re.compile(r"<[a-zA-Z][\w-]*\s[^<>]*?\bdata-screen=([\"'])([^\"']+)\1[^<>]*>")
VARIANT_ATTR_RE = re.compile(r"\sdata-variant=([\"'])([^\"']+)\1")


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
            by_variant.setdefault(vm.group(2), set()).add(m.group(2))
        else:
            shared.add(m.group(2))
    return shared, by_variant


def check_variants(html: str, report: Report) -> tuple[list[str | None], str | None]:
    """Validate the variants manifest. Returns the variant ids (or [None] for one design)
    and the chosen variant, once the PM has picked one at the prototype gate."""
    manifest, err = json_block(html, "prototype-variants")
    _, by_variant = prototype_screens(html)
    if err:
        report.error(f"prototype-variants block is not valid JSON: {err}")
        return [None], None
    if manifest is None:
        if by_variant:
            report.error("screens use data-variant but there is no "
                         '<script type="application/json" id="prototype-variants"> block')
        else:
            report.warn("one design only: build-prototype expects 2 hypothesis-led variants "
                        "(one is fine for an Enhancement; declare it in a prototype-variants block)")
        return list(by_variant) or [None], None

    if not str(manifest.get("decision", "")).strip():
        report.error("prototype-variants: 'decision' must state the trade-off the variants argue about")
    variants = manifest.get("variants")
    if not isinstance(variants, list) or not variants:
        report.error("prototype-variants: 'variants' must be a non-empty list")
        return list(by_variant) or [None], None
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
        for vid in ids:
            if vid in RESERVED_HASHES or vid.startswith("comment-"):
                report.error(f"variant id '{vid}' is reserved by claude.ai links; pick another")
    chosen = manifest.get("chosen")
    if chosen is not None and chosen not in ids:
        report.error(f"prototype-variants: chosen '{chosen}' is not a declared variant")
        chosen = None
    report.note(f"{len(ids)} variant(s): {', '.join(ids)}"
                + (f"; chosen: {chosen} (others archived)" if chosen else ""))
    return ids, chosen


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
                     tree_lines: set, report: Report, chosen: str | None = None) -> None:
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
        if chosen and variant and variant != chosen and status == "open":
            report.error(f"{aid}: variant '{variant}' is archived; review notes now apply to '{chosen}' "
                         "(dismiss this one or reopen the choice)")
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


class _ScreenText(html_parser.HTMLParser):
    """Collect the text inside [data-screen] elements: the product UI, not the side panel."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        if self.depth or any(k == "data-screen" for k, _ in attrs):
            self.depth += 1

    def handle_endtag(self, tag):
        if self.depth and tag not in self.VOID:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.text.append(data)


ICON_GLYPHS = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u25A0-\u25FF\u2B00-\u2BFF]")


def craft_warnings(html: str, report: Report) -> None:
    """Cheap, static checks for the most common tells (reference/prototype-craft.md §6)."""
    parser = _ScreenText()
    try:
        parser.feed(html)
    except Exception:  # an unparsable page is reported elsewhere
        return
    glyphs = sorted(set(ICON_GLYPHS.findall("".join(parser.text))))
    if glyphs:
        report.warn(f"product screens use emoji or symbols as icons ({' '.join(glyphs)}): draw them "
                    "as inline SVG (prototype-craft.md §6)")
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I))
    if re.search(r"background-clip\s*:\s*text", styles):
        report.warn("gradient text (background-clip: text): use weight or size for emphasis")
    if re.search(r"outline\s*:\s*(none|0)\b", styles) and ":focus-visible" not in styles:
        report.warn("focus outlines are removed with no :focus-visible style: keyboard users lose their place")
    if ":focus-visible" not in styles and ":focus" not in styles:
        report.warn("no focus style: add a visible :focus-visible ring from the palette")
    if re.search(r"border-(left|right)\s*:\s*([2-9]|\d{2,})px", styles):
        report.warn("a coloured side border thicker than 1px reads as a generated-design tell")


def cmd_prototype(trees_dir: str, html_path: str) -> int:
    report = Report(f"prototype {html_path}")
    trees = load_trees(Path(trees_dir), Report("(tree parse)"))
    html_file = Path(html_path)
    if not html_file.is_file():
        report.error(f"prototype not found: {html_path}")
        return report.finish()
    html = read(html_file)
    variants, chosen = check_variants(html, report)
    craft_warnings(html, report)
    archived = [v for v in variants if v and chosen and v != chosen]
    if chosen:
        variants = [chosen]
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
    no_demo = 0
    for t in trees:
        entries = cov.get(t["key"])
        if entries is None:
            report.error(f"{t['key']}: tree missing from coverage map")
            continue
        mapped = {}
        for e in entries:
            line = (e.get("line") or "").strip()
            mapped[line] = e
            if not e.get("demo"):
                no_demo += 1
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
    scope = f"the chosen variant ({chosen})" if chosen else "every variant"
    report.note(f"{covered}/{total} tree outcomes demonstrated or justified in {scope}")
    if archived:
        report.note(f"archived, not checked: {', '.join(archived)}")
    if no_demo:
        report.warn(f"{no_demo} coverage line(s) have no 'demo': the coverage panel and deep links "
                    "cannot open them")

    prd_path = html_file.parent.parent / "02-prd.md"
    if prd_path.is_file():
        s6 = section_text(parse_prd(prd_path, Report("(prd parse)")), 6).lower()
        chosen_lines = [ln for ln in s6.splitlines() if "chosen" in ln]
        if chosen:
            man, _ = json_block(html, "prototype-variants")
            label = next((str(v.get("label", "")) for v in man.get("variants", [])
                          if isinstance(v, dict) and v.get("id") == chosen), chosen).lower()
            if not chosen_lines:
                report.error(f"the manifest says '{chosen}' was chosen, but PRD §6.3 does not record "
                             "the choice and why")
            elif not any(label in ln or chosen in ln for ln in chosen_lines):
                report.error(f"PRD §6.3 records a different choice than the manifest's '{chosen}'")
        if not chosen and "chosen at the prototype gate" in s6:
            report.error("PRD §6.3 records a chosen variant, but the prototype-variants manifest has "
                         "no 'chosen'")

    amend = html_file.parent / "amendments.md"
    if amend.is_file():
        tree_lines = {ln for t in trees for ln in t["lines"]}
        all_variants = [v for v in variants + archived]
        check_amendments(amend, all_variants, shared, by_variant, tree_lines, report, chosen)
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


def prd_metrics(prd: dict) -> list[str]:
    """Metric names from the first column of the PRD §7 table(s)."""
    names = []
    for ln in prd["sections"].get(7, {}).get("lines", []):
        if not ln.strip().startswith("|"):
            continue
        cell = ln.strip().strip("|").split("|")[0].strip()
        if not cell or set(cell) <= set("-: ") or cell.lower() == "metric":
            continue
        name = re.sub(r"\*|\(.*?\)", "", cell)
        name = re.sub(r"^\s*guardrail\s*:\s*", "", name, flags=re.I).strip(" .")
        if name:
            names.append(name)
    return names


def cmd_tickets(trees_dir: str, tickets_path: str, prd_path: str | None = None) -> int:
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

    if prd_path:
        prd = parse_prd(Path(prd_path), Report("(prd parse)"))
        text = read(path).lower()
        metrics = prd_metrics(prd)
        for m in metrics:
            if m.lower() not in text:
                report.error(f"PRD §7 metric '{m}' has no analytics event in the tickets "
                             "(name the metric in the analytics story)")
        report.note(f"{len(metrics)} PRD §7 metric(s) checked against the analytics story")

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
    roadmap = root / "roadmap.md"
    if roadmap.is_file():
        text = read(roadmap)
        for idea in sorted((root / "work").glob("*/01-idea.md")):
            st = LEGACY_STAGES.get(item_stage(idea) or "", item_stage(idea) or "")
            if st not in ("parked", "launched") and idea.parent.name not in text:
                report.warn(f"work/{idea.parent.name} ({st}) is not on roadmap.md: run the roadmap skill")
    tools_md = root / "context" / "tools.md"
    if tools_md.is_file():
        reg = parse_registry(tools_md)
        if reg["format"] == "legacy":
            report.warn("context/tools.md uses the 0.4 one-row-per-need format: run setup in repair mode to convert it")
        elif reg["format"] is None:
            report.warn("context/tools.md has no Need | Tool table (see reference/connectors.md)")
        for e in reg["errors"]:
            report.error(f"context/tools.md {e}")
        for w in reg["warnings"]:
            report.warn(f"context/tools.md: {w}")
        skills = find_skills(base=root)
        if reg["format"] and skills:
            quiet = Report("")
            for g in merged_needs(sorted(skills), skills, quiet):
                if g["level"] == "required" and not any(tools_for(reg, n) for n in g["ids"]):
                    report.warn(f"no tool for {join_or(g['ids'])} (required by "
                                f"{', '.join(sorted(g['required_by']))}): add one to context/tools.md")
    design = root / "DESIGN.md"
    if not design.is_file():
        report.warn("missing DESIGN.md: prototypes have no design system (run setup in repair mode)")
    elif "<Product name>" in read(design):
        report.warn("DESIGN.md is still the blank template: run the setup skill to fill it")
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
        lm = re.search(r"^lineage:\s*(\S+)", read(idea), re.M)
        if lm and not (root / "work" / lm.group(1) / "01-idea.md").is_file():
            report.warn(f"work/{item}: lineage '{lm.group(1)}' is not an item in work/")
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


# ---------------------------------------------------------------- needs and the tools registry

NEEDS = {  # need id -> usual source; reference/connectors.md explains each one
    "meeting-notes": "internal", "team-chat": "internal", "support-feedback": "internal",
    "product-analytics": "internal", "governed-metrics": "internal", "web-research": "external",
    "market-data": "external", "docs": "internal", "design-source": "internal",
    "issue-tracker": "internal", "prd-publishing": "internal", "artifact-sharing": "internal",
    "calendar": "internal", "email": "internal",
}
ROLES = ("main", "also", "fallback")
SOURCES = ("internal", "external")
NEED_LINE_RE = re.compile(r"^- (.+?) · (required|optional) · (.+)$")
LEGACY_NEEDS = (  # 0.4 tools.md row labels -> need ids
    ("meeting", ("meeting-notes",)), ("chat", ("team-chat",)), ("support", ("support-feedback",)),
    ("analytics", ("product-analytics",)), ("research", ("web-research",)),
    ("warehouse", ("governed-metrics",)), ("governed", ("governed-metrics",)),
    ("tracker", ("issue-tracker",)), ("prd publishing", ("prd-publishing",)),
    ("sharing", ("artifact-sharing",)), ("wiki", ("docs",)), ("design", ("design-source",)),
    ("calendar", ("calendar", "email")),
)


def parse_needs(text: str) -> dict | None:
    """The `## Needs` block of a SKILL.md: need groups, Includes:, or None."""
    m = re.search(r"^## Needs\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    out = {"groups": [], "includes": [], "none": False, "errors": []}
    lines: list[str] = []
    for ln in m.group(1).splitlines():
        prev = lines[-1] if lines else ""
        if ln.strip() and (ln.startswith(" ") or ln.startswith("`")) and (
                prev.startswith("- ") or prev.startswith("Includes:")):
            lines[-1] += " " + ln.strip()
        else:
            lines.append(ln.strip())
    for ln in lines:
        if ln.lower().startswith("none"):
            out["none"] = True
        elif ln.startswith("Includes:"):
            out["includes"] = re.findall(r"`([a-z0-9-]+)`", ln)
        elif ln.startswith("- "):
            lm = NEED_LINE_RE.match(ln)
            ids = re.findall(r"`([a-z0-9-]+)`", lm.group(1)) if lm else []
            rest = re.sub(r"`[a-z0-9-]+`|,|\bor\b", "", lm.group(1)).strip() if lm else "x"
            if not lm or not ids or rest:
                out["errors"].append(f"cannot read need line: {ln[:70]}")
                continue
            out["groups"].append({"ids": ids, "level": lm.group(2), "why": lm.group(3)})
    return out


def parse_registry(path: Path) -> dict:
    """context/tools.md as rows of need, tool, role, source, trusted; also reads the 0.4 format."""
    reg = {"rows": [], "format": None, "errors": [], "warnings": []}
    if not path.is_file():
        return reg
    header, fenced = None, False
    for n, raw in enumerate(read(path).splitlines(), 1):
        ln = raw.strip()
        if ln.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if not ln.startswith("|"):
            if header is not None and reg["rows"]:
                break
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if header is None:
            low = [c.lower() for c in cells]
            if low and low[0].startswith("need") and len(low) > 1 and low[1].startswith("tool"):
                header = low
                reg["format"] = "registry" if "role" in low and "source" in low else "legacy"
            continue
        if set(ln) <= set("|-: "):
            continue
        row = dict(zip(header, cells))
        need, tool = row.get(header[0], ""), row.get(header[1], "")
        if reg["format"] == "legacy":
            label = need.lower()
            ids = next((v for k, v in LEGACY_NEEDS if k in label), ())
            tools = [t.strip() for t in re.split(r",|\band\b|\+|/", tool) if t.strip()]
            for i, t in enumerate(tools):
                for nid in ids:
                    reg["rows"].append({"need": nid, "tool": t, "role": "main" if i == 0 else "also",
                                        "source": NEEDS[nid], "trusted": "", "line": n})
            continue
        role = (row.get("role") or "").lower()
        source = (row.get("source") or "").lower()
        if need not in NEEDS:
            reg["errors"].append(f"line {n}: unknown need '{need}' (see reference/connectors.md)")
            continue
        if not tool:
            continue
        if role not in ROLES:
            reg["errors"].append(f"line {n}: {need} · {tool}: role must be one of {', '.join(ROLES)}")
        if source not in SOURCES:
            reg["errors"].append(f"line {n}: {need} · {tool}: source must be internal or external")
        trusted = next((v for k, v in row.items() if k.startswith("trusted")), "")
        reg["rows"].append({"need": need, "tool": tool, "role": role, "source": source,
                            "trusted": trusted, "line": n})
    if reg["format"] == "registry":
        for nid in NEEDS:
            roles = [r["role"] for r in reg["rows"] if r["need"] == nid]
            if roles.count("main") > 1:
                reg["warnings"].append(f"{nid}: {roles.count('main')} tools are 'main'; make the others 'also'")
            if roles and "main" not in roles:
                reg["warnings"].append(f"{nid}: has tools but no 'main' one")
    return reg


def join_or(ids: list[str]) -> str:
    return ids[0] if len(ids) == 1 else ", ".join(ids[:-1]) + " or " + ids[-1]


def tools_for(reg: dict, need: str) -> list[dict]:
    rows = [r for r in reg["rows"] if r["need"] == need]
    return sorted(rows, key=lambda r: ROLES.index(r["role"]) if r["role"] in ROLES else 9)


def skill_dirs(extra: str | None = None, base: Path = Path(".")) -> list[Path]:
    """Where SKILL.md files may live: given, workspace, this script's repo, the Claude plugin."""
    here = Path(__file__).resolve().parent
    cands = [Path(extra)] if extra else []
    cands += [base / ".agents" / "skills", base / ".claude" / "skills", here.parent / "skills"]
    if os.environ.get("CLAUDE_PLUGIN_ROOT"):
        cands.append(Path(os.environ["CLAUDE_PLUGIN_ROOT"]) / "skills")
    plugins = Path.home() / ".claude" / "plugins"
    if plugins.is_dir():
        found = [d for pattern in ("cache/*/pm-harness/*/skills", "marketplaces/pm-harness/skills")
                 for d in plugins.glob(pattern) if (d / "capture-idea" / "SKILL.md").is_file()]
        cands += sorted(found, key=lambda d: d.stat().st_mtime, reverse=True)
    return [d for d in cands if d.is_dir()]


def find_skills(extra: str | None = None, base: Path = Path(".")) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for d in skill_dirs(extra, base):
        for s in sorted(d.glob("*/SKILL.md")):
            found.setdefault(s.parent.name, s)
    return found


def merged_needs(names: list[str], skills: dict[str, Path], report: Report) -> list[dict]:
    """The need groups of the named skills (Includes: expanded), strongest level wins."""
    merged: dict[tuple, dict] = {}
    seen: set[str] = set()

    def visit(name: str, top: str) -> None:
        if name in seen:
            return
        seen.add(name)
        path = Path(name) if name.endswith(".md") or "/" in name else skills.get(name)
        if path and path.is_dir():
            path = path / "SKILL.md"
        if not path or not path.is_file():
            report.error(f"skill '{name}' not found; pass the path to its SKILL.md")
            return
        label = path.parent.name
        block = parse_needs(read(path))
        if block is None:
            report.warn(f"{label}: SKILL.md has no ## Needs section")
            return
        for e in block["errors"]:
            report.error(f"{label}: {e}")
        for g in block["groups"]:
            for nid in g["ids"]:
                if nid not in NEEDS:
                    report.error(f"{label}: unknown need '{nid}' (reference/connectors.md)")
            key = tuple(g["ids"])
            m = merged.setdefault(key, {"ids": g["ids"], "level": "optional", "users": [],
                                        "required_by": [], "why": g["why"]})
            if g["level"] == "required":
                m["level"] = "required"
                if label not in m["required_by"]:
                    m["required_by"].append(label)
            if label not in m["users"]:
                m["users"].append(label)
        for inc in block["includes"]:
            visit(inc, top)

    for n in names:
        visit(n, n)
    return sorted(merged.values(), key=lambda g: (g["level"] != "required", g["ids"]))


def cmd_needs(*args: str) -> int:
    names, tools, extra = [], "context/tools.md", None
    it = iter(args)
    for a in it:
        if a == "--tools":
            tools = next(it, tools)
        elif a == "--skills":
            extra = next(it, None)
        else:
            names.append(a)
    if not names:
        print(__doc__)
        return 2
    skills = find_skills(extra, Path(tools).resolve().parent.parent)
    if names == ["all"]:
        names = sorted(skills)
    report = Report(f"needs {' '.join(names) if len(names) < 4 else f'{len(names)} skills'}")
    reg = parse_registry(Path(tools))
    if reg["format"] is None:
        report.warn(f"{tools} not found or has no Need | Tool table: every need is unconfigured")
    elif reg["format"] == "legacy":
        report.warn(f"{tools} uses the 0.4 one-row-per-need format: run setup in repair mode to convert it")
    for e in reg["errors"]:
        report.error(f"{tools} {e}")
    for w in reg["warnings"]:
        report.warn(f"{tools}: {w}")
    groups = merged_needs(names, skills, report)
    wide = max((len(join_or(g["ids"])) for g in groups), default=10)
    for g in groups:
        parts = []
        for nid in g["ids"]:
            ts = tools_for(reg, nid)
            shown = ", ".join(f"{t['tool']} ({t['role']}{', external' if t['source'] == 'external' else ''})" for t in ts)
            parts.append(f"{nid}: {shown or 'no tool'}" if len(g["ids"]) > 1 else (shown or "no tool"))
        users = f"  [{', '.join(g['users'])}]" if len(names) > 1 or g["users"] != names else ""
        report.note(f"{g['level']:<8}  {join_or(g['ids']):<{wide}}  {' · '.join(parts)}{users}")
        if g["level"] == "required" and not any(tools_for(reg, nid) for nid in g["ids"]):
            report.error(f"required {join_or(g['ids'])} has no tool in {tools}: "
                         f"connect one (setup) or plan to finish {', '.join(g['required_by'])} by hand")
    if not groups:
        report.note("no outside needs: works from the workspace files")
    else:
        report.note("next: confirm each tool answers with one read call (reference/connectors.md, preflight)")
    return report.finish()


# ---------------------------------------------------------------- board

NEXT_STEP = {
    "idea": "product-grill if the idea is fuzzy, then write-prd (opportunity-brief to size it first)",
    "prd": "write-behaviour-trees",
    "trees": "build-prototype",
    "prototype": "create-eng-tickets",
    "tickets": "hand over 05-contracts/ to engineering; stakeholder-update",
    "building": "stakeholder-update; set stage launched when it ships",
    "launched": "launch-readout when the gate window ends; then the next phase or done",
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
        blocking = open_blocking(files["review"]) + open_blocking(idea.parent / "03-trees-review.md")
        if blocking:
            flags.append(f"{blocking} open blocking review finding(s)")
        if files["amendments"].is_file():
            open_a = sum(1 for a in parse_amendments(files["amendments"])
                         if a.get("status", "").lower() == "open")
            if open_a:
                flags.append(f"{open_a} open prototype amendment(s): review-prototype")
        if stage != "parked":
            failed = [name for name, code, _ in item_checks(idea.parent) if code]
            if failed:
                flags.append(f"checks failing: {', '.join(failed)} (run pm_check.py item work/{idea.parent.name})")
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
    reg = parse_registry(ctx / "tools.md")
    skills = find_skills(base=root) if reg["format"] else {}
    if skills:
        quiet = Report("")
        missing = [join_or(g["ids"]) for g in merged_needs(sorted(skills), skills, quiet)
                   if g["level"] == "required" and not any(tools_for(reg, n) for n in g["ids"])]
        if missing:
            print(f"Needs with no tool in context/tools.md: {'; '.join(missing)} "
                  "(run pm_check.py workspace . for the skills they block)")
        if reg["format"] == "legacy":
            print("context/tools.md uses the old format: offer to convert it (setup, repair mode)")
    print("Reminders: follow AGENTS.md and the evidence rules; never write to an external tool "
          "without the PM's approval; run done at the end of a useful session.")
    return 0


# ---------------------------------------------------------------- design (DESIGN.md)

DESIGN_SECTIONS = ("Overview", "Colors", "Typography", "Layout", "Elevation & Depth", "Shapes",
                   "Components", "Do's and Don'ts")


def design_tokens(text: str) -> tuple[dict, list[str]] | None:
    """Read DESIGN.md's YAML frontmatter into dotted token paths. Small subset: nested maps of
    scalars, which is all the format uses."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    tokens: dict[str, str] = {}
    problems: list[str] = []
    stack: list[tuple[int, str]] = []
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if ":" not in raw:
            problems.append(f"frontmatter line is not 'key: value': {raw.strip()}")
            continue
        key, value = raw.strip().split(":", 1)
        key = key.strip().strip("'\"")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join([k for _, k in stack] + [key])
        value = value.split(" #", 1)[0].strip().strip("'\"")
        if value:
            tokens[path] = value
        else:
            stack.append((indent, key))
    return tokens, problems


def cmd_design(design_path: str) -> int:
    path = Path(design_path)
    report = Report(f"design system {design_path}")
    if not path.is_file():
        report.error(f"{design_path} not found")
        return report.finish()
    text = read(path)
    parsed = design_tokens(text)
    if parsed is None:
        report.warn("no YAML frontmatter: prototypes have no tokens to use")
        tokens = {}
    else:
        tokens, problems = parsed
        for pr in problems:
            report.error(pr)
        placeholders = [k for k, v in tokens.items() if "<" in v and ">" in v]
        if placeholders:
            report.warn(f"{len(placeholders)} token(s) still hold template placeholders (e.g. "
                        f"{placeholders[0]}): run the setup skill to fill DESIGN.md")
        for k, v in tokens.items():
            for ref in re.findall(r"\{([\w.-]+)\}", v):
                if ref not in tokens:
                    report.error(f"{k}: refers to {{{ref}}}, which is not defined")
        for k in tokens:
            if k.startswith("colors.") and "<" not in tokens[k] and not re.match(
                    r"^(#[0-9a-fA-F]{3,8}|(rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\(.*\))$", tokens[k]):
                report.warn(f"{k}: '{tokens[k]}' does not look like a CSS colour")
    found = [h for h in re.findall(r"^## (.+?)\s*$", text, re.M) if h in DESIGN_SECTIONS]
    order = [DESIGN_SECTIONS.index(h) for h in found]
    if order != sorted(order):
        report.error("sections must keep the canonical order: " + ", ".join(DESIGN_SECTIONS))
    empty = [h for h in found
             if not re.sub(r"<!--.*?-->", "", re.split(rf"^## {re.escape(h)}\s*$", text, flags=re.M)[1]
                           .split("\n## ", 1)[0], flags=re.S).strip()]
    if empty:
        report.warn(f"empty section(s): {', '.join(empty)}")
    groups = sorted({k.split(".", 1)[0] for k in tokens if "." in k})
    report.note(f"{len(tokens)} tokens ({', '.join(groups) or 'none'}), {len(found)} sections")
    return report.finish()


# ---------------------------------------------------------------- item

def run_quiet(fn, *args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = fn(*args)
    return code, buf.getvalue()


def item_checks(folder: Path) -> list[tuple[str, int, str]]:
    """Run every check whose inputs exist for one item. Returns (name, exit code, output)."""
    files = item_files(folder)
    trees = files["trees"] if files["trees"].is_dir() else None
    prd = files["prd"] if files["prd"].is_file() and files["prd"].name == "02-prd.md" else None
    results = []
    if prd:
        results.append(("prd", *run_quiet(cmd_prd, str(prd), str(trees) if trees else None)))
    if trees:
        results.append(("trees", *run_quiet(cmd_trees, str(trees))))
        if files["prototype"].is_file():
            results.append(("prototype", *run_quiet(cmd_prototype, str(trees), str(files["prototype"]))))
        if files["tickets"].is_file():
            results.append(("tickets", *run_quiet(cmd_tickets, str(trees), str(files["tickets"]),
                                                  str(prd) if prd else None)))
    return results


def cmd_item(item_dir: str) -> int:
    folder = Path(item_dir)
    idea = folder / "01-idea.md"
    if not idea.is_file():
        print(f"FAIL  item {item_dir}: no 01-idea.md")
        return 1
    stage = LEGACY_STAGES.get(item_stage(idea) or "", item_stage(idea) or "?")
    results = item_checks(folder)
    for _, _, output in results:
        print(output, end="")
    failed = [name for name, code, _ in results if code]
    ran = ", ".join(name for name, _, _ in results) or "nothing to check yet"
    print(f"{'FAIL' if failed else 'PASS'}  item {folder.name} (stage: {stage}): ran {ran}"
          + (f"; failing: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


# ---------------------------------------------------------------- contracts (engineering hand-off)

def prd_non_goals(prd: dict) -> list[str]:
    goals, on = [], False
    for ln in prd["sections"].get(4, {}).get("lines", []):
        t = ln.strip()
        if re.match(r"^(\*\*|#+\s*)non-goals", t, re.I):
            on = True
            continue
        if on and (t.startswith("**") or t.startswith("#")):
            break
        if on and re.match(r"^[-*]\s+\S", t):
            goals.append(t[2:].strip().rstrip("."))
    return goals


def cmd_contracts(item_dir: str) -> int:
    """Write work/<item>/05-contracts/<subject>.contract.md for the engineering harness."""
    folder = Path(item_dir)
    report = Report(f"contracts for {folder.name}")
    if not folder.is_dir():
        report.error(f"{folder} is not an item folder")
        return report.finish()
    files = item_files(folder)
    trees = load_trees(files["trees"], report)
    prd = parse_prd(files["prd"], Report("(prd parse)")) if files["prd"].is_file() else None
    by_tree: dict[str, dict] = {}
    if prd:
        for c in prd["capabilities"]:
            for t in c["trees"]:
                by_tree[t] = c
    non_goals = prd_non_goals(prd) if prd else []
    out = folder / "05-contracts"
    out.mkdir(exist_ok=True)
    for t in trees:
        cap = by_tree.get(t["key"])
        if t["kind"] == "Journey":
            seam = (prd or {}).get("journey_seam") or "end to end, in a production-like environment"
            source = "PRD §6.1"
        else:
            seam = (cap or {}).get("seam")
            source = f"PRD §{cap['num']}" if cap else "PRD §5"
            if not seam:
                report.warn(f"{t['key']}: no 'Seam:' line under its capability in PRD §5; "
                            "the contract says 'seam: to confirm with engineering'")
                seam = "to confirm with engineering"
        body = ["  " * (depth - 1) + text for (_, depth, _, text) in t["nodes"]]
        lines = [f"Contract: {t['subject']} (seam: {seam})", "", *body, ""]
        if non_goals:
            lines.append("Non-goals: " + "; ".join(non_goals))
        rel = t["path"].relative_to(folder).as_posix() if folder in t["path"].parents else t["path"].name
        lines.append(f"Source: PM Harness item {folder.name}, {rel}, {source}")
        (out / f"{t['subject']}.contract.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        report.note(f"05-contracts/{t['subject']}.contract.md (seam: {seam})")
    return report.finish()


# ---------------------------------------------------------------- artifact

def cmd_artifact(src: str, dest: str) -> int:
    """Turn a full HTML document into the page fragment a Claude artifact publishes."""
    html = read(Path(src))
    if not re.search(r"<html[\s>]", html, re.I):
        Path(dest).write_text(html, encoding="utf-8")
        print(f"PASS  {src} is already a fragment; copied to {dest}")
        return 0
    head = re.search(r"<head[^>]*>(.*?)</head>", html, re.S | re.I)
    body = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
    if not body:
        print(f"FAIL  {src}: no <body>")
        return 1
    parts = []
    head_html = head.group(1) if head else ""
    title = re.search(r"<title>.*?</title>", head_html, re.S | re.I)
    if title:
        parts.append(title.group(0))
    if "safe-area-inset-left" in html:
        parts.append('<meta name="claude:viewport-fit-sides" content="cover">')
    for m in re.finditer(r"<link\b[^>]*>|<style\b.*?</style>|<script\b.*?</script>", head_html, re.S | re.I):
        parts.append(m.group(0))
    parts.append(body.group(1).strip())
    Path(dest).write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"PASS  wrote {dest}: publish it as a Claude artifact")
    return 0


# ---------------------------------------------------------------- view (behaviour trees, visual)

VIEW_KIND_LABEL = {"when": "When", "while": "While", "if": "If", "then": "Then", "and": "And"}


def ticket_map(path: Path) -> dict[str, str]:
    """Tree line -> ticket key, from the fenced acceptance criteria in 05-tickets.md."""
    found, key = {}, None
    for ln in read(path).splitlines():
        hm = re.match(r"^##\s+([A-Z][A-Z0-9]*-\d+)\b", ln)
        if hm:
            key = hm.group(1)
            continue
        t = ln.strip()
        if key and t.split(" ", 1)[0] in KEYWORDS:
            found.setdefault(t, key)
    return found


def node_id(key: str, chain: list[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(chain[-1].lower().split()[:6])).strip("-")
    digest = hashlib.sha1("\n".join([key, *chain]).encode("utf-8")).hexdigest()[:5]
    return f"{key.replace('/', '-')}--{slug}-{digest}"


def cmd_view(item_dir: str) -> int:
    """Write work/<item>/03-trees-view.html: the behaviour trees as a diagram the PM can review."""
    from html import escape as esc
    folder = Path(item_dir)
    report = Report(f"trees view for {folder.name}")
    files = item_files(folder)
    trees = load_trees(files["trees"], report)
    if not trees:
        return report.finish()
    idea = folder / "01-idea.md"
    title = folder.name.replace("-", " ").capitalize()
    if idea.is_file():
        tm = re.search(r"^title:\s*(.+)$", read(idea), re.M)
        title = tm.group(1).strip() if tm else title
    prd = parse_prd(files["prd"], Report("(prd parse)")) if files["prd"].name == "02-prd.md" and files["prd"].is_file() else None
    caps = {t: c for c in (prd or {}).get("capabilities", []) for t in c["trees"]}

    coverage, variant, proto_base = {}, None, None
    if files["prototype"].is_file():
        html = read(files["prototype"])
        cov, _ = json_block(html, "tree-coverage")
        man, _ = json_block(html, "prototype-variants")
        coverage = (cov or {}).get("trees", {}) if isinstance(cov, dict) else {}
        if isinstance(man, dict):
            variant = man.get("chosen") or ((man.get("variants") or [{}])[0] or {}).get("id")
        proto_base = (prd or {}).get("links", {}).get("prototype") or "04-prototype/index.html"
    tickets = ticket_map(files["tickets"]) if files["tickets"].is_file() else {}

    total = demonstrated = in_tickets = warnings = 0
    sections, toc = [], []
    for t in trees:
        cov_by_line = {(e.get("line") or "").strip(): e for e in coverage.get(t["key"], [])}
        cap = caps.get(t["key"])
        if cap:
            where = f"PRD §{esc(cap['num'])} · {esc(PRIORITY_RE.sub('', cap['title']).strip())}" + (
                f" · {esc(cap['priority'])}" if cap.get("priority") else "")
            seam = cap.get("seam")
        elif t["kind"] == "Journey":
            where, seam = "PRD §6.1 · Core journey", (prd or {}).get("journey_seam")
        else:
            where, seam = "Not named in the PRD", None
        chips = "".join(f'<span class="chip">{esc(c.strip())}</span>' for c in t["coverage"].split(";"))
        # nest the (lineno, depth, word, text) nodes, then render them recursively
        root: dict = {"depth": 0, "children": []}
        stack = [root]
        for n in t["nodes"]:
            item = {"n": n, "depth": n[1], "children": []}
            while stack[-1]["depth"] >= n[1]:
                stack.pop()
            stack[-1]["children"].append(item)
            stack.append(item)
        leaves = 0

        def render(items: list, chain: list) -> str:
            nonlocal leaves, total, demonstrated, in_tickets, warnings
            html_out = []
            for it in items:
                lineno, depth, word, text = it["n"]
                here = chain + [text]
                nid = node_id(t["key"], here)
                clause = esc(text.split(" ", 1)[1] if " " in text else text)
                badges = []
                if word in LEAF_WORDS:
                    leaves += 1
                    total += 1
                    e = cov_by_line.get(text)
                    if e and e.get("screen"):
                        demonstrated += 1
                        frag = "--".join(x for x in (variant, e["screen"], e.get("demo")) if x)
                        badges.append(f'<a class="badge proto" href="{esc(proto_base)}#{esc(frag)}" '
                                      f'target="_blank" rel="noopener">Prototype: {esc(e["screen"])}</a>')
                    elif e and e.get("reason"):
                        demonstrated += 1
                        badges.append(f'<span class="badge">Not on screen: {esc(e["reason"])}</span>')
                    elif coverage:
                        badges.append('<span class="badge warn">Not in the prototype</span>')
                    if text in tickets:
                        in_tickets += 1
                        badges.append(f'<span class="badge ticket">{esc(tickets[text])}</span>')
                    for vague in VAGUE:
                        if re.search(rf"\b{re.escape(vague)}\b", f" {text.lower()} "):
                            warnings += 1
                            badges.append(f'<span class="badge warn">\u201c{esc(vague)}\u201d is hard to test</span>')
                kids = render(it["children"], here) if it["children"] else ""
                html_out.append(
                    f'<li class="node k-{word}"><div class="clause" id="{nid}" data-comment-target '
                    f'data-tree="{esc(t["key"])}" data-line="{lineno}" data-text="{esc(text)}">'
                    f'<span class="kw">{VIEW_KIND_LABEL[word]}</span><span class="txt">{clause}</span>'
                    + (f'<span class="badges">{"".join(badges)}</span>' if badges else "")
                    + '<button type="button" class="cbtn">Comment</button></div>'
                    + (f'<ol class="kids">{kids}</ol>' if kids else "") + "</li>")
            return "".join(html_out)

        out = [render(root["children"], [])]
        anchor = f"tree-{t['kind'].lower()}-{t['subject']}"
        toc.append(f'<a href="#{anchor}"><span class="tk k-{t["kind"].lower()}">{esc(t["kind"])}</span>'
                   f'{esc(t["subject"])}</a>')
        sections.append(
            f'<details class="tree-card" id="{anchor}" open><summary>'
            f'<span class="tk k-{t["kind"].lower()}">{esc(t["kind"])}</span>'
            f'<span class="subject">{esc(t["subject"])}</span>'
            f'<span class="where">{where}</span><span class="count">{leaves} outcomes</span></summary>'
            f'<div class="meta">{chips}' + (f'<span class="seam">Seam: {esc(seam)}</span>' if seam else "")
            + f'<span class="file">{esc(t["path"].name)}</span></div>'
            f'<div class="diagram"><ol class="tree">{"".join(out)}</ol></div></details>'
        )

    stats = [("Trees", str(len(trees))), ("Outcomes", str(total))]
    if coverage:
        stats.append(("In the prototype", f"{demonstrated}/{total}"))
    if tickets:
        stats.append(("In tickets", f"{in_tickets}/{total}"))
    stats.append(("Hard to test", str(warnings)))
    phase = (prd or {}).get("phase")
    page = (VIEW_TEMPLATE
            .replace("__TITLE__", esc(f"{title} trees"))
            .replace("__HEADING__", esc(title))
            .replace("__PHASE__", f'<span class="phase">{esc(phase)}</span>' if phase else "")
            .replace("__ITEM__", esc(folder.name))
            .replace("__STATS__", "".join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in stats))
            .replace("__TOC__", "".join(toc))
            .replace("__TREES__", "\n".join(sections)))
    dest = folder / "03-trees-view.html"
    dest.write_text(page, encoding="utf-8")
    report.note(f"wrote {dest.name}: {len(trees)} trees, {total} outcomes")
    return report.finish()


VIEW_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">
<style>
/* Layout: a header with the counts, then one card per tree; each tree reads left to right,
   cause to outcome, and stacks into an indented outline on a phone. */
:root {
  --bg: #f5f6f8; --surface: #ffffff; --ink: #14171c; --muted: #5a6472; --line: #d3d9e1;
  --accent: #4d6378; --focus: #2f6fe0; --warn: #9a5800; --warn-bg: #fbf0dc;
  --when: #2c5b8a; --when-bg: #e8eff7; --while: #67499f; --while-bg: #efeaf8;
  --if: #8a5a00; --if-bg: #f8eedb; --then: #1d6e46; --then-bg: #e4f2ea;
  --font: "Geist", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0e1013; --surface: #161a1f; --ink: #e7ebf0; --muted: #9aa4b1; --line: #2b323b;
  --accent: #8fa3b8; --focus: #7aa7ff; --warn: #f0b860; --warn-bg: #2a2214;
  --when: #93bbe8; --when-bg: #15212d; --while: #bba6ec; --while-bg: #1e1929;
  --if: #efbb62; --if-bg: #272013; --then: #72d2a2; --then-bg: #12231b; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0e1013; --surface: #161a1f; --ink: #e7ebf0; --muted: #9aa4b1; --line: #2b323b;
  --accent: #8fa3b8; --focus: #7aa7ff; --warn: #f0b860; --warn-bg: #2a2214;
  --when: #93bbe8; --when-bg: #15212d; --while: #bba6ec; --while-bg: #1e1929;
  --if: #efbb62; --if-bg: #272013; --then: #72d2a2; --then-bg: #12231b; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 14px/1.5 var(--font); }
.page { max-width: 1280px; margin: 0 auto; padding-block: 28px 96px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: flex; flex-direction: column; gap: 20px; }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
header { display: flex; flex-direction: column; gap: 12px; }
.eyebrow { font: 500 12px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
h1 { margin: 0; font-size: 28px; font-weight: 500; letter-spacing: -0.015em; text-wrap: balance;
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.phase { font: 500 12px/1 var(--mono); border: 1px solid var(--line); border-radius: 999px; padding: 6px 10px; color: var(--muted); }
dl.stats { display: flex; flex-wrap: wrap; gap: 8px 28px; margin: 0; }
dl.stats div { display: flex; flex-direction: column; gap: 2px; }
dt { font-size: 12px; color: var(--muted); }
dd { margin: 0; font: 500 18px/1.2 var(--mono); font-variant-numeric: tabular-nums; }
.howto { color: var(--muted); max-width: 72ch; margin: 0; }
.howto b { color: var(--ink); font-weight: 500; }
.mode-local { display: inline; } .has-comments .mode-local { display: none; }
.mode-artifact { display: none; } .has-comments .mode-artifact { display: inline; }
.legend, .toc { display: flex; flex-wrap: wrap; gap: 8px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); }
.legend i { font: 500 11px/1 var(--mono); padding: 4px 6px; border-radius: 6px; font-style: normal; }
.toc a { display: inline-flex; gap: 8px; align-items: center; text-decoration: none; color: var(--ink);
  border: 1px solid var(--line); background: var(--surface); border-radius: 999px; padding: 6px 12px; font-size: 13px; }
.toc a:hover { border-color: var(--accent); }
.tk { font: 500 10px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.tree-card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; }
.tree-card > summary { list-style: none; cursor: pointer; display: flex; flex-wrap: wrap; align-items: baseline;
  gap: 6px 14px; padding: 16px 18px; }
.tree-card > summary::-webkit-details-marker { display: none; }
.tree-card > summary::before { content: "▸"; color: var(--muted); transition: transform .15s; }
.tree-card[open] > summary::before { transform: rotate(90deg); }
.subject { font: 500 16px/1.3 var(--mono); }
.where { color: var(--muted); }
.count { margin-left: auto; color: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 18px 12px; align-items: center; }
.chip, .seam, .file { font: 400 12px/1 var(--mono); color: var(--muted); }
.chip { border: 1px dashed var(--line); border-radius: 6px; padding: 4px 6px; }
.seam { color: var(--ink); }
.file { margin-left: auto; }
.diagram { overflow-x: auto; padding: 4px 18px 18px; border-top: 1px solid var(--line); }
/* the tree: each node is its clause card followed by its children */
ol.tree, ol.kids { list-style: none; margin: 0; padding: 0; }
ol.tree { padding-top: 12px; }
.node { display: flex; align-items: flex-start; padding: 5px 0; }
.clause { position: relative; flex: 0 0 auto; width: 17.5rem; display: flex; flex-wrap: wrap; gap: 4px 8px;
  align-items: baseline; background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
  padding: 8px 10px; scroll-margin: 80px; }
.kw { font: 500 11px/1.6 var(--mono); letter-spacing: .04em; text-transform: uppercase; padding: 0 6px; border-radius: 5px; }
.txt { flex: 1 1 12rem; min-width: 0; }
.k-when > .clause .kw, .legend .k-when { color: var(--when); background: var(--when-bg); }
.k-while > .clause .kw, .legend .k-while { color: var(--while); background: var(--while-bg); }
.k-if > .clause .kw, .legend .k-if { color: var(--if); background: var(--if-bg); }
.k-then > .clause .kw, .k-and > .clause .kw, .legend .k-then { color: var(--then); background: var(--then-bg); }
.k-then > .clause, .k-and > .clause { background: color-mix(in srgb, var(--then-bg) 45%, var(--surface)); }
.badges { flex-basis: 100%; display: flex; flex-wrap: wrap; gap: 6px; }
.badge { font: 400 11px/1.4 var(--mono); border-radius: 6px; padding: 2px 6px; border: 1px solid var(--line);
  color: var(--muted); text-decoration: none; max-width: 100%; overflow-wrap: anywhere; }
a.badge.proto { color: var(--accent); }
a.badge.proto:hover { border-color: var(--accent); }
.badge.ticket { color: var(--ink); }
.badge.warn { color: var(--warn); background: var(--warn-bg); border-color: transparent; }
.cbtn { position: absolute; top: -11px; right: 8px; font: 500 11px/1 var(--font); color: var(--muted);
  background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 5px 8px; cursor: pointer;
  opacity: 0; transition: opacity .12s; }
.clause:hover .cbtn, .clause:focus-within .cbtn, .clause.noted .cbtn { opacity: 1; }
@media (hover: none) { .cbtn { opacity: 1; } }
.cbtn:hover { color: var(--ink); border-color: var(--accent); }
.clause.noted { border-color: var(--accent); }
/* connectors */
ol.kids { position: relative; padding-left: 28px; margin-top: -5px; }
ol.kids::before { content: ""; position: absolute; left: 0; top: 24px; width: 14px; border-top: 1.5px solid var(--line); }
ol.kids > .node { position: relative; }
ol.kids > .node::before { content: ""; position: absolute; left: -14px; top: 24px; width: 14px; border-top: 1.5px solid var(--line); }
ol.kids > .node::after { content: ""; position: absolute; left: -14px; top: 0; bottom: 0; border-left: 1.5px solid var(--line); }
ol.kids > .node:first-child::after { top: 24px; }
ol.kids > .node:last-child::after { bottom: auto; height: 24px; }
ol.kids > .node:only-child::after { display: none; }
@media (max-width: 760px) {
  .node { display: block; }
  .clause { width: auto; }
  ol.kids { margin: 0 0 0 12px; padding-left: 18px; }
  ol.kids::before { display: none; }
  ol.kids > .node::before { left: -18px; width: 16px; top: 22px; }
  ol.kids > .node::after { left: -18px; }
  ol.kids > .node:first-child::after { top: 0; }
  ol.kids > .node:last-child::after { height: 22px; }
  ol.kids > .node:only-child::after { display: block; top: 0; height: 22px; }
  .file { margin-left: 0; }
}
/* note editor and tray (used when this page is not a Claude artifact) */
.note-edit { flex-basis: 100%; display: flex; flex-direction: column; gap: 6px; margin-top: 4px; }
.note-edit textarea { width: 100%; min-height: 64px; font: inherit; color: var(--ink); background: var(--bg);
  border: 1px solid var(--line); border-radius: 8px; padding: 6px 8px; resize: vertical; }
.row { display: flex; gap: 6px; flex-wrap: wrap; }
.btn { font: 500 12px/1 var(--font); border-radius: 999px; padding: 7px 12px; cursor: pointer;
  border: 1px solid var(--line); background: var(--surface); color: var(--ink); }
.btn.primary { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.note-text { flex-basis: 100%; font-size: 13px; color: var(--ink); border-left: 2px solid var(--accent); padding-left: 8px; }
.tray { position: fixed; left: 0; right: 0; bottom: 0; background: var(--surface); border-top: 1px solid var(--line);
  padding-block: 10px calc(10px + env(safe-area-inset-bottom, 0px));
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.tray-inner { max-width: 1280px; margin: 0 auto; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.tray pre { flex-basis: 100%; max-height: 30vh; overflow: auto; margin: 0; font: 12px/1.5 var(--mono);
  white-space: pre-wrap; background: var(--bg); border-radius: 8px; padding: 8px; }
footer { color: var(--muted); font-size: 12px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div class="page">
<header>
  <div class="eyebrow">Behaviour trees · __ITEM__</div>
  <h1>__HEADING__ __PHASE__</h1>
  <dl class="stats">__STATS__</dl>
  <p class="howto">Read each tree left to right: an event, the state the user is in, a condition, then what they see.
    <span class="mode-artifact"><b>Comment</b> on any line and choose <b>Send to Claude</b>: Claude changes the tree
    file and republishes this page.</span><span class="mode-local"><b>Comment</b> on any line, then
    <b>Copy for Claude</b> and paste the notes into your chat.</span></p>
  <div class="legend"><span><i class="k-when">When</i>an event</span><span><i class="k-while">While</i>a state that holds</span>
    <span><i class="k-if">If</i>a condition</span><span><i class="k-then">Then / And</i>an outcome, which becomes a test</span></div>
  <nav class="toc" aria-label="Trees">__TOC__</nav>
</header>
__TREES__
<footer>Generated from the tree files by PM Harness. Change the trees, not this page.</footer>
</div>
<div class="tray" id="tray" hidden><div class="tray-inner">
  <b id="tray-count"></b>
  <button type="button" class="btn primary" id="tray-copy">Copy for Claude</button>
  <button type="button" class="btn" id="tray-clear">Clear notes</button>
  <pre id="tray-out" hidden></pre>
</div></div>
<script>
(function () {
  "use strict";
  var comments = null;
  var notes = [];
  if (window.claude && typeof window.claude.use === "function") {
    window.claude.use("comments").then(function (c) {
      if (c) { comments = c; document.documentElement.classList.add("has-comments"); }
    }, function () {});
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".cbtn");
    if (!btn) return;
    var clause = btn.closest(".clause");
    if (comments) {
      comments.openComposer({ element: clause }).catch(function (err) {
        if (err && (err.code === "unavailable" || err.code === "not_granted")) {
          comments = null; document.documentElement.classList.remove("has-comments"); editNote(clause);
        }
      });
    } else { editNote(clause); }
  });
  function editNote(clause) {
    if (clause.querySelector(".note-edit")) { clause.querySelector("textarea").focus(); return; }
    var box = document.createElement("div");
    box.className = "note-edit";
    var area = document.createElement("textarea");
    area.id = "note-" + clause.id;
    area.setAttribute("aria-label", "Note on this line");
    area.placeholder = "What should change, and why?";
    var row = document.createElement("div"); row.className = "row";
    var add = document.createElement("button"); add.type = "button"; add.className = "btn primary"; add.textContent = "Add note";
    var cancel = document.createElement("button"); cancel.type = "button"; cancel.className = "btn"; cancel.textContent = "Cancel";
    row.appendChild(add); row.appendChild(cancel); box.appendChild(area); box.appendChild(row);
    clause.appendChild(box); area.focus();
    cancel.addEventListener("click", function () { box.remove(); });
    add.addEventListener("click", function () {
      var text = area.value.trim();
      if (!text) { area.focus(); return; }
      notes.push({ tree: clause.dataset.tree, line: clause.dataset.line, text: clause.dataset.text, note: text });
      box.remove();
      var shown = document.createElement("div"); shown.className = "note-text"; shown.textContent = text;
      clause.appendChild(shown); clause.classList.add("noted");
      renderTray();
    });
  }
  function renderTray() {
    document.getElementById("tray").hidden = !notes.length;
    document.getElementById("tray-count").textContent = notes.length + (notes.length === 1 ? " note" : " notes");
    document.getElementById("tray-out").hidden = true;
  }
  function asText() {
    return ["Behaviour tree review: please change the trees, re-run the checks and regenerate the view."]
      .concat(notes.map(function (n, i) {
        return (i + 1) + ". " + n.tree + " line " + n.line + ": " + n.text + "\n   Note: " + n.note;
      })).join("\n");
  }
  document.getElementById("tray-copy").addEventListener("click", function () {
    var out = document.getElementById("tray-out"), btn = this, text = asText();
    out.textContent = text;
    var select = function () {
      out.hidden = false;
      var r = document.createRange(); r.selectNodeContents(out);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      btn.textContent = "Selected: press Ctrl/⌘+C";
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "Copied: paste into your chat";
        setTimeout(function () { btn.textContent = "Copy for Claude"; }, 2000);
      }, select);
    } else { select(); }
  });
  document.getElementById("tray-clear").addEventListener("click", function () {
    notes = [];
    document.querySelectorAll(".note-text").forEach(function (n) { n.remove(); });
    document.querySelectorAll(".clause.noted").forEach(function (c) { c.classList.remove("noted"); });
    renderTray();
  });
})();
</script>
</body>
</html>
"""


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
        block = parse_needs(text)
        if block is None:
            report.error(f"skills/{name}: no ## Needs section (reference/connectors.md §5)")
        else:
            for e in block["errors"]:
                report.error(f"skills/{name}: {e}")
            for g in block["groups"]:
                for nid in g["ids"]:
                    if nid not in NEEDS:
                        report.error(f"skills/{name}: unknown need '{nid}'")
            for inc in block["includes"]:
                if inc not in names:
                    report.error(f"skills/{name}: Includes unknown skill '{inc}'")
            if not (block["groups"] or block["none"] or block["includes"]):
                report.error(f"skills/{name}: ## Needs is empty; write 'None: …' if it has no outside needs")
            for other in re.findall(r"pm_check\.py needs ([a-z0-9-]+)", text):
                if other not in (name, "all"):
                    report.error(f"skills/{name}: its preflight runs 'needs {other}'")
    agents = sorted((root / "agents").glob("*.md"))
    for a in agents:
        fm = frontmatter(a)
        if not fm or not fm.get("name") or not fm.get("description"):
            report.error(f"agents/{a.name}: needs name and description frontmatter")
        elif fm["name"] != a.stem:
            report.error(f"agents/{a.name}: name '{fm['name']}' must equal file name")
    for doc in ("reference/connectors.md", "templates/workspace/context/tools.md"):
        if (root / doc).is_file():
            missing = [n for n in NEEDS if f"`{n}`" not in read(root / doc) and f"| {n} |" not in read(root / doc)]
            if missing:
                report.error(f"{doc} does not list need(s): {', '.join(missing)}")
    template = root / "templates" / "workspace"
    if template.is_dir() and not is_workspace(template):
        report.error(f"templates/workspace: AGENTS.md or CLAUDE.md needs the {MARKER} marker")
    report.note(f"{len(skills)} skills, {len(agents)} agents, version {next(iter(versions.values()), '?')}")
    return report.finish()


def main(argv: list[str]) -> int:
    commands = {
        "item": (cmd_item, (1,)),
        "view": (cmd_view, (1,)),
        "contracts": (cmd_contracts, (1,)),
        "artifact": (cmd_artifact, (2,)),
        "prd": (cmd_prd, (1, 2)),
        "trees": (cmd_trees, (1,)),
        "prototype": (cmd_prototype, (2,)),
        "tickets": (cmd_tickets, (2, 3)),
        "workspace": (cmd_workspace, (1,)),
        "design": (cmd_design, (1,)),
        "board": (cmd_board, (1,)),
        "plugin": (cmd_plugin, (1,)),
        "needs": (cmd_needs, None),
    }
    if len(argv) < 2 or argv[1] not in commands or (
            commands[argv[1]][1] is not None and len(argv) - 2 not in commands[argv[1]][1]):
        print(__doc__)
        return 2
    fn, _ = commands[argv[1]]
    return fn(*argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
