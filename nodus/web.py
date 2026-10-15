"""JSON views for the website's pages. No HTTP here: nodus/../api/server.py serves these.

Each function reads one sandbox graph and returns plain data. Matching, severity, wording, the
SVG drawing and the melody all come from the same tested modules the Streamlit app uses.
"""
from pathlib import Path

from nodus.agent import acknowledge, echo_id, echo_record, messages_for, on_plan_saved, track_record
from nodus.baseline import keyword_ranking
from nodus.lessons import active_lessons, approve, lesson_detail, list_lessons, load_lesson_file, reject
from nodus.matcher import evaluate
from nodus.melody import melody_events, melody_wav
from nodus.plans import add_step, list_plans, people, plan_facts, remove_step, set_follows, set_gate
from nodus.severity import is_warning, level
from nodus.svg import alignment_svg, shape_strip
from nodus.view import rows_for
from nodus.witnesses import route, sources

ROOT = Path(__file__).resolve().parent.parent


def _states(lesson, result):
    states = [(c.holds, s["kind"] == "absent") for c, s in zip(result.conditions, lesson["conditions"])]
    comp = [c["id"] for c in lesson["conditions"]].index(lesson["completion"])
    return states, comp


def plans_overview(g):
    lessons = active_lessons(g)
    plans = []
    for pid, title, summary, risk, owner in list_plans(g):
        rows = []
        for les in lessons:
            r = evaluate(g, pid, les)
            lvl = level(r.k, r.n, r.missing, les["completion"])
            states, comp = _states(les, r)
            rows.append({"lesson": les["id"], "name": les["name"], "origin": les["origin"],
                         "k": r.k, "n": r.n, "level": lvl, "warning": is_warning(lvl),
                         "strip": shape_strip(states, comp)})
        plans.append({"id": pid, "title": title, "summary": summary, "risk": risk,
                      "owner": owner, "lessons": rows,
                      "at_risk": any(x["warning"] for x in rows)})
    plans.sort(key=lambda p: (not p["at_risk"], p["title"]))
    count = lambda lvl: sum(any(x["level"] == lvl for x in p["lessons"]) for p in plans)
    return {"plans": plans, "lessons": len(lessons), "one_step": count("foresight"),
            "full": count("full"), "at_risk": sum(p["at_risk"] for p in plans)}


def plan_detail(g, plan_id):
    f = plan_facts(g, plan_id)
    return {"steps": [{"id": i, "kind": k, "scope": s} for i, k, s, _ in f["steps"]],
            "follows_canary": any(p == "proc-canary" for p, _ in f["follows"]),
            "peer_review": any(c == "chk-human" for c, *_ in f["gates"])}


def save_plan(g, plan_id, follows, reviewed, add=None, remove=()):
    set_follows(g, plan_id, "proc-canary", follows)
    set_gate(g, plan_id, "chk-human", reviewed)
    for sid in remove:
        remove_step(g, sid)
    if add:
        add_step(g, plan_id, add["kind"], add["scope"])
    return [{"lesson": r["lesson_id"], "name": r["lesson_name"], "level": r["level"],
             "k": r["k"], "n": r["n"]} for r in on_plan_saved(g, plan_id)]


def echo(g, plan_id, lesson_id):
    lessons = {l["id"]: l for l in active_lessons(g)}
    les = lessons[lesson_id]
    title = next(p[1] for p in list_plans(g) if p[0] == plan_id)
    r = evaluate(g, plan_id, les)
    lvl = level(r.k, r.n, r.missing, les["completion"])
    detail = lesson_detail(g, lesson_id)
    completion = next(c["text"] for c in les["conditions"] if c["id"] == les["completion"])
    states, comp = _states(les, r)
    rec = echo_record(g, echo_id(lesson_id, plan_id))
    w = route(g, lesson_id, plan_id) if les["origin"] != "public" else None
    return {"plan": {"id": plan_id, "title": title},
            "lesson": {"id": lesson_id, "name": les["name"], "origin": les["origin"]},
            "k": r.k, "n": r.n, "level": lvl, "completion": completion,
            "completion_missing": not states[comp][0],
            "svg": alignment_svg(les["name"], title, rows_for(g, plan_id, les, r), r.k, r.n, lvl),
            "headsup": rec and {"text": rec[0], "silences": rec[1] or [], "status": rec[2],
                                "outcome": rec[3], "seen": rec[4]},
            "witness": w and {"name": w.name, "reason": w.reason, "rule": w.rule},
            "sources": sources(g, lesson_id) if les["origin"] == "public" else [],
            "conditions": detail,
            "lessons": [{"id": l["id"], "name": l["name"]} for l in lessons.values()]}


def melody(g, plan_id, lesson_id, resolve=False):
    les = next(l for l in active_lessons(g) if l["id"] == lesson_id)
    states, comp = _states(les, evaluate(g, plan_id, les))
    return melody_wav(melody_events(lesson_id, states, comp, resolve))


def inbox(g, person_id):
    keys = ["echo_id", "plan_id", "plan", "lesson_id", "lesson", "origin", "level", "k", "n",
            "headsup", "silences", "status", "outcome", "reason", "is_owner"]
    return [dict(zip(keys, row)) for row in messages_for(g, person_id)]


def people_list(g):
    return [{"id": i, "name": n} for i, n, active in people(g) if active]


def record_answer(g, eid, person_name, outcome, reason):
    acknowledge(g, eid, person_name, outcome, reason)


def lessons_view(g):
    out = []
    for lid, name, origin, status, version, by in list_lessons(g):
        out.append({"id": lid, "name": name, "origin": origin, "status": status,
                    "version": version, "approved_by": by, "track": track_record(g, lid),
                    "conditions": lesson_detail(g, lid)})
    return out


def set_lesson_status(g, lesson_id, approved, by):
    (approve if approved else reject)(g, lesson_id, by)


def compare(g):
    overview = plans_overview(g)
    names = {}
    files = sorted((ROOT / "data" / "lessons").glob("*.json"))
    lessons = [load_lesson_file(f) for f in files]
    for les in lessons:
        names[les.id] = les.name
    plans = [(p["id"], p["title"], p["summary"]) for p in overview["plans"]]
    raised = {p["id"]: [x["name"] for x in p["lessons"] if x["warning"]] for p in overview["plans"]}
    titles = {p["id"]: p["title"] for p in overview["plans"]}
    return [{"plan": titles[pid], "closest_by_words": names.get(lid, lid),
             "similarity": round(sim, 3), "nodus_raises": raised[pid]}
            for pid, lid, sim in keyword_ranking(lessons, plans)]
