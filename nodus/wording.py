"""Every sentence NODUS shows is filled in from match results. No free-form AI text.

Absences are always worded as "not recorded in the company graph": NODUS can only see
what was recorded, so it never says "you forgot".
"""
from nodus.db import read


def names(graph, ids):
    rows = read(graph, "MATCH (n) WHERE n.id IN $ids RETURN n.id, coalesce(n.title, n.name, n.id)",
                {"ids": list(ids)})
    return dict(rows)


def silence_lines(graph, lesson, result):
    """One line per absence condition that holds, naming the entity it is about."""
    label = names(graph, result.bindings.values())
    lines = []
    for spec, res in zip(lesson["conditions"], result.conditions):
        if spec["kind"] != "absent" or not res.holds:
            continue
        about = None
        if spec["start"].startswith("role:"):
            about = result.bindings.get(spec["start"][5:])
        elif "role" in spec.get("target", {}):
            about = result.bindings.get(spec["target"]["role"])
        what = f' ("{label.get(about, about)}")' if about else ""
        lines.append(f"∅ Not recorded in the company graph: {spec['text'].lower()}{what}.")
    return lines


def ownerless(graph, entity_id):
    """A supporting silence: the bound entity has no active owner recorded."""
    rows = read(graph, "MATCH (x {id: $id}) RETURN size([(p:Person {active: true})-[o:OWNS]->(x) | p])",
                {"id": entity_id})
    return bool(rows) and rows[0][0] == 0


def headsup(plan_title, lesson_name, k, n, lvl, missing_text, witness_line):
    if lvl == "foresight":
        first = (f'"{plan_title}" already has {k} of the {n} conditions of "{lesson_name}". '
                 f"The remaining one is the step that would complete it: {missing_text.lower()}. "
                 f"Consider not taking that step as planned.")
    elif lvl == "full":
        first = (f'"{plan_title}" has all {n} conditions of "{lesson_name}". '
                 f"The shape of this past failure is complete in the plan.")
    else:
        first = (f'"{plan_title}" has {k} of the {n} conditions of "{lesson_name}". '
                 f"Missing: {missing_text.lower()}.")
    return first + (f" {witness_line}" if witness_line else "")
