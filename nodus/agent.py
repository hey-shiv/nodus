"""The agent loop (plan B9): observe -> match -> decide -> act -> (human) -> remember.

on_plan_saved() runs when a plan is created or changed. Matching is read-only. The only
writes are Echo records (the agent's memory) and, later, outcomes from a human.
The agent never edits a plan, never approves a lesson, and never sends a message itself.
"""
import json
import time

from nodus.db import read
from nodus.lessons import active_lessons
from nodus.matcher import evaluate
from nodus.severity import is_warning, level
from nodus.witnesses import route, sources
from nodus.wording import headsup, names, ownerless, silence_lines

OUTCOMES = ("heeded", "dismissed", "escalated")


def echo_id(lesson_id, plan_id):
    """Stable identity: the same lesson on the same plan is one echo, however often it's seen."""
    return f"echo:{lesson_id}:{plan_id}"


def _plan_title(graph, plan_id):
    rows = read(graph, "MATCH (p:Plan {id: $id}) RETURN p.title", {"id": plan_id})
    return rows[0][0] if rows else plan_id


def on_plan_saved(graph, plan_id, now=None):
    now = now or int(time.time())
    title = _plan_title(graph, plan_id)
    report = []
    for lesson in active_lessons(graph):                                   # OBSERVE
        result = evaluate(graph, plan_id, lesson)                         # MATCH (read-only)
        lvl = level(result.k, result.n, result.missing, lesson["completion"])   # DECIDE
        eid = echo_id(lesson["id"], plan_id)
        if not is_warning(lvl):
            _clear(graph, eid, now)
            continue
        texts = {c["id"]: c["text"] for c in lesson["conditions"]}       # ACT
        witness = route(graph, lesson["id"], plan_id) if lesson["origin"] != "public" else None
        srcs = sources(graph, lesson["id"]) if lesson["origin"] == "public" else []
        witness_line = (f"Invited: {witness.name}, who {witness.reason}." if witness
                        else "Sources: " + "; ".join(s["publisher"] for s in srcs) if srcs
                        else "No witness available.")
        missing_text = "; ".join(texts[m] for m in result.missing) or "nothing"
        silences = silence_lines(graph, lesson, result)
        label = names(graph, result.bindings.values())
        silences += [f'∅ Not recorded in the company graph: an active owner for "{label.get(v, v)}".'
                     for v in result.bindings.values() if v.startswith("ch-") and ownerless(graph, v)]
        text = headsup(title, lesson["name"], result.k, result.n, lvl, missing_text, witness_line)
        _remember(graph, eid, lesson, plan_id, result, lvl, text, silences, witness, now)  # REMEMBER
        report.append({"echo_id": eid, "lesson_id": lesson["id"], "lesson_name": lesson["name"],
                       "level": lvl, "k": result.k, "n": result.n, "missing": result.missing,
                       "headsup": text, "silences": silences, "witness": witness,
                       "sources": srcs})
    return report


def _remember(graph, eid, lesson, plan_id, result, lvl, text, silences, witness, now):
    graph.query(
        "MATCH (l:Lesson {id: $lid}), (p:Plan {id: $pid}) "
        "MERGE (e:Echo {id: $eid}) "
        "ON CREATE SET e.created_at = $now, e.times_seen = 0 "
        "SET e.k = $k, e.n = $n, e.level = $level, e.missing = $missing, e.holding = $holding, "
        "e.bindings = $bindings, e.headsup = $text, e.silences = $silences, "
        "e.lesson_version = $version, e.updated_at = $now, e.times_seen = e.times_seen + 1, "
        "e.status = CASE WHEN e.outcome IS NULL THEN 'open' ELSE 'acknowledged' END "
        "MERGE (e)-[:OF_LESSON]->(l) MERGE (e)-[:ON_PLAN]->(p)",
        {"lid": lesson["id"], "pid": plan_id, "eid": eid, "now": now, "k": result.k,
         "n": result.n, "level": lvl, "missing": result.missing,
         "holding": [c.id for c in result.conditions if c.holds],
         "bindings": json.dumps(result.bindings), "text": text, "silences": silences,
         "version": lesson.get("version", 1)})
    graph.query("MATCH (e:Echo {id: $eid})-[i:INVITED]->() DELETE i", {"eid": eid})
    if witness:
        graph.query("MATCH (e:Echo {id: $eid}), (p:Person {id: $pid}) MERGE (e)-[:INVITED]->(p)",
                    {"eid": eid, "pid": witness.person_id})


def _clear(graph, eid, now):
    """The plan changed and no longer echoes the lesson: keep the record, mark it cleared."""
    if read(graph, "MATCH (e:Echo {id: $id}) RETURN e.id", {"id": eid}):
        graph.query("MATCH (e:Echo {id: $id}) WHERE e.status = 'open' "
                    "SET e.status = 'cleared', e.updated_at = $now", {"id": eid, "now": now})


def acknowledge(graph, eid, by, outcome, reason="", now=None, categorise=None):
    """The human step: the plan owner says what they did about the echo.

    categorise: optional function reason -> (category, confidence), e.g. Laya
    (nodus.suggest.categorise_reason). Only used to sort dismissal reasons for the track record.
    """
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome must be one of {OUTCOMES}")
    if outcome == "dismissed" and not reason.strip():
        raise ValueError("a dismissal needs a reason")
    category, conf = (categorise(reason) if categorise and outcome == "dismissed"
                      else (None, None))
    graph.query("MATCH (e:Echo {id: $id}) SET e.outcome = $outcome, e.reason = $reason, "
                "e.reason_category = $category, e.reason_category_conf = $conf, "
                "e.acknowledged_by = $by, e.acknowledged_at = $at, e.status = 'acknowledged'",
                {"id": eid, "outcome": outcome, "reason": reason, "by": by, "category": category,
                 "conf": conf, "at": now or int(time.time())})


def track_record(graph, lesson_id):
    """How this lesson's echoes went: raised, heeded, dismissed (with reasons), escalated, open."""
    rows = read(graph, "MATCH (e:Echo)-[o:OF_LESSON]->(l:Lesson {id: $id}) "
                       "RETURN e.status, e.outcome, e.reason, e.reason_category", {"id": lesson_id})
    record = {"raised": len(rows), "heeded": 0, "dismissed": 0, "escalated": 0, "open": 0,
              "reasons": [], "reason_categories": {}}
    for status, outcome, reason, category in rows:
        if outcome:
            record[outcome] += 1
            if outcome == "dismissed":
                record["reasons"].append(reason)
                if category:
                    cats = record["reason_categories"]
                    cats[category] = cats.get(category, 0) + 1
        elif status == "open":
            record["open"] += 1
    return record


def inbox(graph):
    """Open and acknowledged echoes, newest first, for the Inbox page."""
    return read(graph,
        "MATCH (e:Echo)-[a:ON_PLAN]->(p:Plan), (e)-[b:OF_LESSON]->(l:Lesson) "
        "OPTIONAL MATCH (e)-[i:INVITED]->(w:Person) "
        "RETURN e.id, p.id, p.title, l.id, l.name, e.level, e.k, e.n, e.headsup, e.status, "
        "e.outcome, e.reason, w.name, e.times_seen, e.updated_at "
        "ORDER BY e.updated_at DESC, e.id")


def observe_all(graph, now=None):
    """Run the loop for every current plan (used when the demo world is (re)loaded)."""
    from nodus.watch import current_plans
    return {plan: on_plan_saved(graph, plan, now) for plan in current_plans(graph)}


def echo_record(graph, eid):
    rows = read(graph, "MATCH (e:Echo {id: $id}) RETURN e.headsup, e.silences, e.status, "
                       "e.outcome, e.times_seen", {"id": eid})
    return rows[0] if rows else None


def messages_for(graph, person_id):
    """Echoes a person should see: on plans they own, or where they were invited."""
    return read(graph,
        "MATCH (e:Echo)-[a:ON_PLAN]->(p:Plan), (e)-[b:OF_LESSON]->(l:Lesson) "
        "WHERE (:Person {id: $pid})-[:OWNS]->(p) OR (e)-[:INVITED]->(:Person {id: $pid}) "
        "OPTIONAL MATCH (owner:Person)-[o:OWNS]->(p) "
        "RETURN e.id, p.id, p.title, l.id, l.name, l.origin, e.level, e.k, e.n, e.headsup, "
        "e.silences, e.status, e.outcome, e.reason, owner.id = $pid AS is_owner "
        "ORDER BY e.updated_at DESC, e.id", {"pid": person_id})
