"""Write world data into FalkorDB idempotently: running it twice changes nothing.

Nodes: UNWIND rows, MERGE on the stable id, SET the properties.
Relationships: MATCH both endpoints by id, then MERGE the relationship.
"""
from collections import defaultdict

from redis.exceptions import ResponseError

from nodus.schema import LABELS, RELATIONSHIPS


def _check(name, allowed):
    if name not in allowed:
        raise ValueError(f"not in the graph model: {name!r}")
    return name


def ensure_indexes(graph, labels):
    """Index every label's id, so MERGE and MATCH by id don't scan all nodes."""
    for label in sorted(labels):
        try:
            graph.query(f"CREATE INDEX FOR (n:{_check(label, LABELS)}) ON (n.id)")
        except ResponseError as e:
            if "already indexed" not in str(e):
                raise


def load(graph, world):
    by_label = defaultdict(list)
    for n in world["nodes"]:
        by_label[n["label"]].append({"id": n["id"], "props": n["props"]})
    ensure_indexes(graph, by_label)
    for label, rows in sorted(by_label.items()):
        graph.query(f"UNWIND $rows AS row MERGE (n:{_check(label, LABELS)} {{id: row.id}}) "
                    f"SET n += row.props", {"rows": rows})

    by_shape = defaultdict(list)
    for r in world["rels"]:
        by_shape[(r["type"], r["from_label"], r["to_label"])].append(
            {"from": r["from"], "to": r["to"]})
    for (type_, fl, tl), rows in sorted(by_shape.items()):
        graph.query(f"UNWIND $rows AS row "
                    f"MATCH (a:{_check(fl, LABELS)} {{id: row.from}}), "
                    f"(b:{_check(tl, LABELS)} {{id: row.to}}) "
                    f"MERGE (a)-[:{_check(type_, RELATIONSHIPS)}]->(b)", {"rows": rows})


def counts(graph):
    """{label: n} and {rel_type: n} as stored, for checking a load."""
    nodes = dict(graph.ro_query("MATCH (n) RETURN labels(n)[0] AS l, count(n) "
                                "ORDER BY l").result_set)
    rels = dict(graph.ro_query("MATCH ()-[r]->() RETURN type(r) AS t, count(r) "
                               "ORDER BY t").result_set)
    return nodes, rels
