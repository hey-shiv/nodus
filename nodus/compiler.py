"""Turn one lesson condition (data) into one parameterized Cypher query.

One hand-written template per condition kind (docs/condition-kinds.md). Every value
travels as a $parameter; every identifier is checked against nodus.schema.
"""
from nodus.schema import LABELS, PROPERTIES, RELATIONSHIPS


class CompileError(ValueError):
    """The condition uses a name or shape the compiler doesn't accept."""


def _ident(name, allowed, what):
    if name not in allowed:
        raise CompileError(f"unknown {what}: {name!r}")
    return name


def _start(cond, anchor, bindings, params):
    """Return (node pattern for s, WHERE clauses) for the condition's start."""
    start = cond["start"]
    if start == "anchor":
        params["start"] = anchor
        return "(s:Plan)", ["s.id = $start"]
    if start.startswith("role:"):
        params["start"] = bindings[start[5:]]
        return "(s)", ["s.id = $start"]
    if start.startswith("other:"):
        params["anchor"] = anchor
        label = _ident(start[6:], LABELS, "label")
        return f"(s:{label})", ["s.id <> $anchor"]
    raise CompileError(f"unknown start: {start!r}")


def _path(cond, anchor, bindings, params):
    """Return (pattern text from s to t, WHERE clauses on t, last relationship name)."""
    hops = cond["path"]
    if not 1 <= len(hops) <= 2:
        raise CompileError("path must have 1 or 2 hops")
    text, where = "(s)", []
    for i, (rel, direction) in enumerate(hops, start=1):
        rel = _ident(rel, RELATIONSHIPS, "relationship")
        node = "t" if i == len(hops) else f"n{i}"
        if i == len(hops):
            target = cond["target"]
            if "role" in target:
                params["target"] = bindings[target["role"]]
                where.append("t.id = $target")
                node_text = "(t)"
            else:
                node_text = f"(t:{_ident(target['label'], LABELS, 'label')})"
                for j, (prop, value) in enumerate(sorted(target.get("props", {}).items())):
                    params[f"tp{j}"] = value
                    where.append(f"t.{_ident(prop, PROPERTIES, 'property')} = $tp{j}")
        else:
            node_text = f"({node})"
        # Relationships are always named (r1, r2): unnamed ones miscount (T06).
        if direction == "out":
            text += f"-[r{i}:{rel}]->{node_text}"
        elif direction == "in":
            text += f"<-[r{i}:{rel}]-{node_text}"
        else:
            raise CompileError(f"unknown direction: {direction!r}")
    return text, where, f"r{len(hops)}"


def compile_condition(cond, anchor, bindings):
    """Return (cypher, params). Every query returns one column `holds` plus `ids`."""
    params = {}
    kind = cond["kind"]
    s_node, s_where = _start(cond, anchor, bindings, params)

    if kind == "attribute_equals":
        prop = _ident(cond["property"], PROPERTIES, "property")
        params["value"] = cond["value"]
        cypher = (f"MATCH {s_node} WHERE {' AND '.join(s_where)} "
                  f"RETURN coalesce(s.{prop} = $value, false) AS holds, [s.id] AS ids")
        return cypher, params

    pattern, t_where, last_rel = _path(cond, anchor, bindings, params)

    if kind == "present":
        where = " AND ".join(s_where + t_where)
        cypher = (f"MATCH {s_node} MATCH {pattern} WHERE {where} "
                  f"WITH DISTINCT t.id AS tid ORDER BY tid "
                  f"RETURN count(tid) > 0 AS holds, collect(tid) AS ids")
    elif kind == "absent":
        t_filter = f" WHERE {' AND '.join(t_where)}" if t_where else ""
        cypher = (f"MATCH {s_node} WHERE {' AND '.join(s_where)} "
                  f"OPTIONAL MATCH {pattern}{t_filter} "
                  f"RETURN count({last_rel}) = 0 AS holds, [s.id] AS ids")
    elif kind == "count_equals":
        params["n"] = cond["n"]
        t_filter = f" WHERE {' AND '.join(t_where)}" if t_where else ""
        bad = []
        for j, (prop, value) in enumerate(sorted(cond.get("all_targets", {}).items())):
            params[f"at{j}"] = value
            bad.append(f"coalesce(t.{_ident(prop, PROPERTIES, 'property')} = $at{j}, false)")
        all_ok = " AND ".join(bad) if bad else "true"
        cypher = (f"MATCH {s_node} WHERE {' AND '.join(s_where)} "
                  f"OPTIONAL MATCH {pattern}{t_filter} "
                  f"WITH count({last_rel}) AS c, "
                  f"sum(CASE WHEN {last_rel} IS NULL OR ({all_ok}) THEN 0 ELSE 1 END) AS bad, "
                  f"collect(DISTINCT t.id) AS ids "
                  f"RETURN c = $n AND bad = 0 AS holds, ids")
    else:
        raise CompileError(f"unknown or unbuilt kind: {kind!r}")
    return cypher, params
