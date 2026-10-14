"""Run every approved lesson against every current plan (plan B5: two stages).

Stage 1 (cheap): skip lessons whose anchor relationships the plan doesn't have at all.
Stage 2 (careful): anchor-first evaluation of every condition (nodus.matcher).
An echo is *raised* when k >= n - 1 (status full, foresight or strong).
"""
from nodus.db import read
from nodus.lessons import active_lessons
from nodus.matcher import evaluate

RAISED = {"full", "foresight", "strong"}


def current_plans(graph):
    return [r[0] for r in read(graph, "MATCH (p:Plan) WHERE p.status IN ['planned', 'in_progress'] "
                                      "RETURN p.id ORDER BY p.id")]


def plan_rel_types(graph, plan_id):
    rows = read(graph, "MATCH (p:Plan {id: $id})-[r]->() RETURN DISTINCT type(r)", {"id": plan_id})
    return {r[0] for r in rows}


def anchor_rel_types(lesson):
    """Relationships a plan must have for any positive anchor condition to hold."""
    return {c["path"][0][0] for c in lesson["conditions"]
            if c["start"] == "anchor" and c["kind"] in ("present", "count_equals")}


def run(graph, lessons=None):
    """[(plan_id, MatchResult)] for every plan x lesson that passes stage 1."""
    lessons = lessons if lessons is not None else active_lessons(graph)
    results = []
    for plan in current_plans(graph):
        has = plan_rel_types(graph, plan)
        for lesson in lessons:
            if anchor_rel_types(lesson) & has:
                results.append((plan, evaluate(graph, plan, lesson)))
    return results


def echoes(results):
    return [(p, r) for p, r in results if r.status in RAISED]
