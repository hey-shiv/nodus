"""Lessons: validate them, store them in FalkorDB, approve them, load the approved ones.

A lesson is data (docs/condition-kinds.md). Before it can be stored it must:
  1. have the right shape (pydantic),
  2. compile: every condition uses only whitelisted names (dry run of the compiler),
  3. cite: every quote appears verbatim in its source document's text.
Only a human approval (approve()) makes a lesson active. The LLM never approves.
"""
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from nodus.compiler import compile_condition
from nodus.db import read
from nodus.schema import ENDS, KIND_BY_LABEL, VOCAB

ROOT = Path(__file__).resolve().parent.parent
SOURCE_CACHE = ROOT / "cache" / "sources"


class Citation(BaseModel):
    doc: str
    quote: str = Field(min_length=10)
    note: str | None = None


class Condition(BaseModel):
    id: str
    text: str
    kind: Literal["present", "absent", "attribute_equals", "count_equals"]
    start: str
    path: list[tuple[str, Literal["out", "in"]]] | None = None
    target: dict | None = None
    bind: str | None = None
    property: str | None = None
    value: str | bool | int | None = None
    n: int | None = None
    all_targets: dict | None = None
    citations: list[Citation] = Field(min_length=1)

    def spec(self):
        """The part the compiler reads (no text, no citations)."""
        return self.model_dump(exclude={"text", "citations"}, exclude_none=True)


class Lesson(BaseModel):
    id: str
    name: str
    origin: Literal["public", "synthetic"]
    summary: str
    safe_pattern: str
    learned_from: list[str] = Field(min_length=1)
    completion: str
    conditions: list[Condition] = Field(min_length=3, max_length=6)

    @model_validator(mode="after")
    def _structure(self):
        ids = [c.id for c in self.conditions]
        if len(ids) != len(set(ids)):
            raise ValueError("condition ids must be unique")
        if self.completion not in ids:
            raise ValueError("completion must name one of the conditions")
        if not any(c.kind == "absent" for c in self.conditions):
            raise ValueError("a lesson needs at least one absence condition")
        role_label = {}
        for c in self.conditions:
            label = _walk(c, role_label)            # type-checks the path; label at the far end
            on_start = _start_label(c, role_label)
            checks = [(label, (c.target or {}).get("props", {})), (label, c.all_targets or {})]
            if c.kind == "attribute_equals":
                checks.append((on_start, {c.property: c.value}))
            for lbl, filters in checks:
                for prop, value in filters.items():
                    if prop not in VOCAB:
                        raise ValueError(f"{c.id} filters on {prop!r}: only controlled-vocabulary "
                                         f"properties are allowed ({sorted(VOCAB)})")
                    allowed = KIND_BY_LABEL.get(lbl, VOCAB[prop]) if prop == "kind" else VOCAB[prop]
                    if value not in allowed:
                        raise ValueError(f"{c.id}: {prop}={value!r} is not in the vocabulary for "
                                         f"{lbl or 'this node'} {sorted(map(str, allowed))}")
            if c.bind:
                role_label[c.bind] = label
            if c.start.startswith("other:") and not (c.kind == "present" and c.bind):
                raise ValueError(f"{c.id}: an 'other:' start only works for a 'present' condition "
                                 f"that binds a role; anything else isn't tied to the plan")
        bound = set()
        for c in self.conditions:
            needed = []
            if c.start.startswith("role:"):
                needed.append(c.start[5:])
            if c.target and "role" in c.target:
                needed.append(c.target["role"])
            missing = [r for r in needed if r not in bound]
            if missing:
                raise ValueError(f"{c.id} uses role(s) {missing} before they are bound")
            if c.bind:
                bound.add(c.bind)
        return self

    def as_matcher_input(self):
        return {"id": self.id, "completion": self.completion,
                "conditions": [{"id": c.id, **c.spec()} for c in self.conditions]}

    def digest(self):
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()[:12]


def _start_label(c, role_label):
    if c.start == "anchor":
        return "Plan"
    if c.start.startswith("other:"):
        return c.start[6:]
    return role_label.get(c.start[5:])


def _walk(c, role_label):
    """Follow the path through ENDS; refuse a hop that can't exist. Returns the far-end label."""
    current = _start_label(c, role_label)
    for rel, direction in c.path or []:
        if rel not in ENDS:
            return None                             # unknown names are refused by the compiler
        src, dst = ENDS[rel]
        here, there = (src, dst) if direction == "out" else (dst, src)
        if current and here and current != here:
            raise ValueError(f"{c.id}: {current} has no {direction}going {rel} relationship "
                             f"({rel} goes from {src or 'any'} to {dst or 'any'})")
        current = there
    target = c.target or {}
    wanted = target.get("label") or role_label.get(target.get("role"))
    if c.path and current and wanted and current != wanted:
        raise ValueError(f"{c.id}: the path ends at {current}, but the target is {wanted}")
    return wanted or current if c.path else _start_label(c, role_label)


def normalise(text):
    """Collapse whitespace and curly quotes so a quote matches however the page wraps."""
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip()


def check_compiles(lesson):
    """Dry-run the compiler on every condition with placeholder ids."""
    fake = {c.bind: "placeholder" for c in lesson.conditions if c.bind}
    for c in lesson.conditions:
        compile_condition({"id": c.id, **c.spec()}, anchor="placeholder", bindings=fake)


def source_text(doc_id, sources):
    """The text a quote must appear in: a synthetic file in the repo, or a cached public page."""
    src = sources[doc_id]
    if "path" in src:
        return normalise((ROOT / src["path"]).read_text())
    cached = SOURCE_CACHE / f"{doc_id}.txt"
    return normalise(cached.read_text()) if cached.exists() else None


def unverified_quotes(lesson, sources):
    """Return [(condition id, doc, problem)] for every quote not found verbatim."""
    problems = []
    for c in lesson.conditions:
        for cit in c.citations:
            if cit.doc not in sources:
                problems.append((c.id, cit.doc, "unknown source"))
                continue
            text = source_text(cit.doc, sources)
            if text is None:
                problems.append((c.id, cit.doc, "source text not cached (run scripts/verify_sources.py)"))
            elif normalise(cit.quote) not in text:
                problems.append((c.id, cit.doc, "quote not found verbatim"))
    return problems


def load_sources():
    return {s["id"]: s for s in json.loads((ROOT / "data" / "sources.json").read_text())}


def load_lesson_file(path):
    return Lesson.model_validate_json(Path(path).read_text())


# ---------- storage in FalkorDB ----------

def store(graph, lesson, sources):
    """Write (or update) a lesson as 'proposed'. A changed lesson gets a new version."""
    check_compiles(lesson)
    digest = lesson.digest()
    rows = read(graph, "MATCH (l:Lesson) WHERE l.id = $id RETURN l.digest, l.version, l.status", {"id": lesson.id})
    if rows and rows[0][0] == digest:
        return rows[0][1]                      # unchanged: keep version and status
    version = rows[0][1] + 1 if rows else 1
    graph.query(
        "MERGE (l:Lesson {id: $id}) SET l.name = $name, l.origin = $origin, l.summary = $summary, "
        "l.safe_pattern = $safe, l.completion = $completion, l.digest = $digest, "
        "l.version = $version, l.status = 'proposed', l.approved_by = null, l.approved_at = null",
        {"id": lesson.id, "name": lesson.name, "origin": lesson.origin, "summary": lesson.summary,
         "safe": lesson.safe_pattern, "completion": lesson.completion, "digest": digest,
         "version": version})
    graph.query("MATCH (l:Lesson {id: $id})-[r:HAS_CONDITION]->(c:Condition) DETACH DELETE c",
                {"id": lesson.id})
    for order, c in enumerate(lesson.conditions, start=1):
        graph.query(
            "MATCH (l:Lesson {id: $lid}) "
            "MERGE (c:Condition {id: $id}) SET c.cid = $cid, c.text = $text, c.kind = $kind, "
            "c.order = $order, c.is_absence = $absence, c.spec = $spec "
            "MERGE (l)-[:HAS_CONDITION]->(c)",
            {"lid": lesson.id, "id": f"{lesson.id}/{c.id}", "cid": c.id, "text": c.text,
             "kind": c.kind, "order": order, "absence": c.kind == "absent",
             "spec": json.dumps(c.spec())})
        for cit in c.citations:
            src = sources[cit.doc]
            graph.query(
                "MATCH (c:Condition {id: $cid}) "
                "MERGE (d:Document {id: $doc}) SET d.title = $title, d.origin = $origin, "
                "d.url = $url, d.publisher = $publisher "
                "MERGE (c)-[r:CITES {quote: $quote}]->(d)",
                {"cid": f"{lesson.id}/{c.id}", "doc": cit.doc, "title": src["title"],
                 "origin": src["origin"], "url": src.get("url"),
                 "publisher": src["publisher"], "quote": cit.quote})
    for ref in lesson.learned_from:
        label = "Episode" if ref.startswith("ep-") else "Document"
        graph.query(f"MATCH (l:Lesson {{id: $id}}) MERGE (x:{label} {{id: $ref}}) "
                    f"MERGE (l)-[:LEARNED_FROM]->(x)", {"id": lesson.id, "ref": ref})
    return version


def approve(graph, lesson_id, approved_by):
    """The human step. Records who and when; only approved lessons are matched."""
    graph.query("MATCH (l:Lesson {id: $id}) SET l.status = 'approved', "
                "l.approved_by = $by, l.approved_at = $at",
                {"id": lesson_id, "by": approved_by, "at": int(time.time())})


def reject(graph, lesson_id, by):
    graph.query("MATCH (l:Lesson {id: $id}) SET l.status = 'rejected', l.approved_by = $by",
                {"id": lesson_id, "by": by})


def list_lessons(graph):
    return read(graph, "MATCH (l:Lesson) RETURN l.id, l.name, l.origin, l.status, l.version, l.approved_by "
        "ORDER BY l.id")


def lesson_detail(graph, lesson_id):
    """Conditions with their citations, for the approval page and the echo page."""
    rows = read(graph, "MATCH (l:Lesson {id: $id})-[h:HAS_CONDITION]->(c:Condition) "
        "OPTIONAL MATCH (c)-[r:CITES]->(d:Document) "
        "RETURN c.cid, c.text, c.kind, c.order, d.id, d.title, d.url, d.origin, r.quote, d.publisher "
        "ORDER BY c.order", {"id": lesson_id})
    out = {}
    for cid, text, kind, order, doc, title, url, origin, quote, publisher in rows:
        entry = out.setdefault(cid, {"id": cid, "text": text, "kind": kind, "citations": []})
        if doc:
            entry["citations"].append({"doc": doc, "title": title, "url": url, "origin": origin,
                                       "quote": quote, "publisher": publisher})
    return list(out.values())


def active_lessons(graph):
    """Approved lessons in the matcher's input shape, read back from the graph."""
    rows = read(graph, "MATCH (l:Lesson {status: 'approved'})-[h:HAS_CONDITION]->(c:Condition) "
        "RETURN l.id, l.name, l.completion, l.origin, l.version, c.cid, c.spec, c.text "
        "ORDER BY l.id, c.order")
    lessons = {}
    for lid, name, completion, origin, version, cid, spec, text in rows:
        les = lessons.setdefault(lid, {"id": lid, "name": name, "completion": completion,
                                       "origin": origin, "version": version, "conditions": []})
        les["conditions"].append({"id": cid, "text": text, **json.loads(spec)})
    return list(lessons.values())
