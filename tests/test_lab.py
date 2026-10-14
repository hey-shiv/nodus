"""T06 lab: verify FalkorDB 6.0.2 behaviours NODUS will depend on.

Each test checks ONE behaviour on a tiny toy graph. A failing test is a finding,
recorded in docs/g1-lab.md, not something to hide.
"""
import pytest
from redis.exceptions import ResponseError


def rows(g, q, params=None):
    return g.query(q, params).result_set


# 1. Counting parallel relationships: named vs unnamed
def test_count_parallel_rels_named(graph):
    graph.query("CREATE (a:N {id:1})-[:R]->(b:N {id:2}), (a)-[:R]->(b)")
    assert rows(graph, "MATCH (:N {id:1})-[r:R]->(:N {id:2}) RETURN count(r)") == [[2]]


def test_count_parallel_rels_unnamed(graph):
    graph.query("CREATE (a:N {id:1})-[:R]->(b:N {id:2}), (a)-[:R]->(b)")
    result = rows(graph, "MATCH (:N {id:1})-[:R]->(:N {id:2}) RETURN count(*)")
    # FINDING (documented limitation, confirmed on 6.0.2): an unnamed relationship is
    # only checked for existence, so two parallel edges count as ONE. Always name it.
    assert result == [[1]]


# 2. Absence: NOT pattern predicate in WHERE
def test_absence_not_pattern(graph):
    graph.query(
        "CREATE (:Plan {id:'owned'})-[:OWNED_BY]->(:Person {id:'p'}), (:Plan {id:'orphan'})"
    )
    got = rows(graph, "MATCH (p:Plan) WHERE NOT (p)-[:OWNED_BY]->(:Person) RETURN p.id")
    assert got == [["orphan"]]


# 3. Relationship-type alternation in one pattern
def test_rel_type_alternation(graph):
    graph.query(
        "CREATE (a:N {id:'a'})-[:SHIPS]->(:N {id:'x'}), (a)-[:PUSHES]->(:N {id:'y'}),"
        " (a)-[:READS]->(:N {id:'z'})"
    )
    got = rows(graph, "MATCH (:N {id:'a'})-[:SHIPS|PUSHES]->(t) RETURN t.id ORDER BY t.id")
    assert got == [["x"], ["y"]]


# 4. DISTINCT inside aggregation
def test_distinct_in_aggregation(graph):
    graph.query(
        "CREATE (a:N {id:'a'})-[:R]->(t:T {name:'svc'}), (a)-[:R]->(t),"
        " (a)-[:R]->(:T {name:'db'})"
    )
    got = rows(
        graph,
        "MATCH (:N {id:'a'})-[:R]->(t:T) "
        "RETURN count(DISTINCT t.name), size(collect(DISTINCT t.name))",
    )
    assert got == [[2, 2]]


# 5a. Time as UTC epoch integers (plan D09 option a)
def test_epoch_int_comparison(graph):
    graph.query(
        "CREATE (:E {id:'early', at:$t1}), (:E {id:'late', at:$t2})",
        {"t1": 1_760_000_000, "t2": 1_760_086_400},
    )
    got = rows(graph, "MATCH (e:E) WHERE e.at > $cut RETURN e.id", {"cut": 1_760_050_000})
    assert got == [["late"]]


# 5b. Native temporal types: do comparisons work on 6.0.2?
def test_native_date_comparison(graph):
    got = rows(graph, "RETURN date('2026-10-15') < date('2026-10-16')")
    assert got == [[True]]


# 6. REMOVE vs SET to null
def test_remove_property(graph):
    graph.query("CREATE (:N {id:1, flag:true})")
    graph.query("MATCH (n:N {id:1}) REMOVE n.flag")
    assert rows(graph, "MATCH (n:N {id:1}) RETURN keys(n)") == [[["id"]]]


def test_set_null_removes_property(graph):
    graph.query("CREATE (:N {id:1, flag:true})")
    graph.query("MATCH (n:N {id:1}) SET n.flag = null")
    assert rows(graph, "MATCH (n:N {id:1}) RETURN keys(n)") == [[["id"]]]


# 7. ro_query rejects writes
def test_ro_query_rejects_write(graph):
    graph.query("CREATE (:N {id:1})")
    with pytest.raises(ResponseError):
        graph.ro_query("CREATE (:N {id:2})")
    assert rows(graph, "MATCH (n:N) RETURN count(n)") == [[1]]


# 8. Undirected patterns return each pair twice
def test_undirected_returns_pair_twice(graph):
    graph.query("CREATE (:N {id:1})-[:R]->(:N {id:2})")
    assert rows(graph, "MATCH (a:N)-[:R]-(b:N) RETURN count(*)") == [[2]]


# 9. Consistent bindings: one variable reused across two patterns = same node
def test_variable_reuse_binds_same_node(graph):
    graph.query(
        "CREATE (alice:P {id:'alice'})-[:OWNS]->(:C {id:'c1'}),"
        " (bob:P {id:'bob'})-[:APPROVES]->(:C {id:'c2'}),"
        " (alice)-[:APPROVES]->(:C {id:'c3'})"
    )
    got = rows(
        graph,
        "MATCH (p:P)-[:OWNS]->(:C), (p)-[:APPROVES]->(:C) RETURN DISTINCT p.id",
    )
    assert got == [["alice"]]
