"""Plan reads and the few edits a plan owner can make in the demo (no Cypher in pages)."""
import time

from nodus.db import read


def list_plans(graph):
    return read(graph,
        "MATCH (p:Plan) WHERE p.status IN ['planned', 'in_progress'] "
        "OPTIONAL MATCH (o:Person)-[r:OWNS]->(p) "
        "RETURN p.id, p.title, p.summary, p.risk_class, o.name ORDER BY p.id")


def plan_facts(graph, plan_id):
    """What the plan is made of, for the owner's editing form."""
    steps = read(graph, "MATCH (p:Plan {id: $id})-[h:HAS_STEP]->(s:Step) "
                        "RETURN s.id, s.kind, s.scope, s.at ORDER BY s.at, s.id", {"id": plan_id})
    gates = read(graph, "MATCH (p:Plan {id: $id})-[g:GATED_BY]->(c:Check) "
                        "RETURN c.id, c.title, c.kind ORDER BY c.id", {"id": plan_id})
    follows = read(graph, "MATCH (p:Plan {id: $id})-[f:FOLLOWS]->(pr:Procedure) "
                          "RETURN pr.id, pr.title ORDER BY pr.id", {"id": plan_id})
    return {"steps": steps, "gates": gates, "follows": follows}


def add_step(graph, plan_id, kind, scope, at=None):
    count = read(graph, "MATCH (p:Plan {id: $id})-[h:HAS_STEP]->(s) RETURN count(h)",
                 {"id": plan_id})[0][0]
    graph.query("MATCH (p:Plan {id: $id}) MERGE (s:Step {id: $sid}) "
                "SET s.kind = $kind, s.scope = $scope, s.at = $at, s.origin = 'synthetic' "
                "MERGE (p)-[:HAS_STEP]->(s)",
                {"id": plan_id, "sid": f"{plan_id}-u{count + 1}", "kind": kind, "scope": scope,
                 "at": at or int(time.time())})


def remove_step(graph, step_id):
    graph.query("MATCH (s:Step {id: $id}) DETACH DELETE s", {"id": step_id})


def set_follows(graph, plan_id, procedure_id, follows):
    if follows:
        graph.query("MATCH (p:Plan {id: $p}), (pr:Procedure {id: $pr}) MERGE (p)-[:FOLLOWS]->(pr)",
                    {"p": plan_id, "pr": procedure_id})
    else:
        graph.query("MATCH (p:Plan {id: $p})-[f:FOLLOWS]->(pr:Procedure {id: $pr}) DELETE f",
                    {"p": plan_id, "pr": procedure_id})


def set_gate(graph, plan_id, check_id, gated):
    if gated:
        graph.query("MATCH (p:Plan {id: $p}), (c:Check {id: $c}) MERGE (p)-[:GATED_BY]->(c)",
                    {"p": plan_id, "c": check_id})
    else:
        graph.query("MATCH (p:Plan {id: $p})-[g:GATED_BY]->(c:Check {id: $c}) DELETE g",
                    {"p": plan_id, "c": check_id})


def people(graph):
    return read(graph, "MATCH (p:Person) RETURN p.id, p.name, p.active ORDER BY p.name")


def owned_plan_ids(graph, person_id):
    return [r[0] for r in read(graph, "MATCH (:Person {id: $id})-[o:OWNS]->(p:Plan) RETURN p.id",
                               {"id": person_id})]
