"""Anchor-first evaluation of one lesson against one plan (plan D08).

Each condition's truth comes from FalkorDB (one read-only query per condition). This
module only orders the conditions, passes bound role ids along, and counts k of n.
"""
from dataclasses import dataclass, field

from nodus.compiler import compile_condition


@dataclass
class ConditionResult:
    id: str
    holds: bool
    state: str            # "holds" | "missing" | "unbound"
    ids: list = field(default_factory=list)


@dataclass
class MatchResult:
    lesson_id: str
    anchor: str
    k: int
    n: int
    status: str           # "full" | "foresight" | "strong" | "partial"
    conditions: list
    bindings: dict

    @property
    def missing(self):
        return [c.id for c in self.conditions if not c.holds]


def _roles_needed(cond):
    roles = []
    if cond["start"].startswith("role:"):
        roles.append(cond["start"][5:])
    if "role" in cond.get("target", {}):
        roles.append(cond["target"]["role"])
    return roles


def _run(graph, conditions, anchor, bindings):
    """Evaluate conditions in order; branch when a binder finds several candidates."""
    if not conditions:
        return [], bindings
    cond, rest = conditions[0], conditions[1:]

    if any(role not in bindings for role in _roles_needed(cond)):
        result = ConditionResult(cond["id"], False, "unbound")
        later, final = _run(graph, rest, anchor, bindings)
        return [result] + later, final

    cypher, params = compile_condition(cond, anchor, bindings)
    rows = graph.ro_query(cypher, params).result_set
    holds, ids = rows[0] if rows else (False, [])   # no rows: the start node doesn't exist
    result = ConditionResult(cond["id"], bool(holds), "holds" if holds else "missing", ids)

    role = cond.get("bind")
    if not (role and holds):
        later, final = _run(graph, rest, anchor, bindings)
        return [result] + later, final

    # One branch per candidate (ids are sorted); keep the highest k, ties -> smallest id.
    best = None
    for candidate in ids:
        later, final = _run(graph, rest, anchor, {**bindings, role: candidate})
        k = sum(c.holds for c in later)
        if best is None or k > best[0]:
            best = (k, later, final)
    return [result] + best[1], best[2]


def _status(k, n, missing, completion):
    if k == n:
        return "full"
    if k == n - 1:
        return "foresight" if missing == [completion] else "strong"
    return "partial"


def evaluate(graph, anchor, lesson):
    # Some conditions are facts about the company, not the plan (A1.2), so they would
    # hold even for a plan that doesn't exist. Check the anchor first.
    found = graph.ro_query("MATCH (p:Plan) WHERE p.id = $anchor RETURN count(p)",
                           {"anchor": anchor}).result_set[0][0]
    if found:
        conditions, bindings = _run(graph, lesson["conditions"], anchor, {})
    else:
        conditions = [ConditionResult(c["id"], False, "unbound") for c in lesson["conditions"]]
        bindings = {}
    k, n = sum(c.holds for c in conditions), len(conditions)
    missing = [c.id for c in conditions if not c.holds]
    return MatchResult(lesson["id"], anchor, k, n,
                       _status(k, n, missing, lesson["completion"]),
                       conditions, bindings)
