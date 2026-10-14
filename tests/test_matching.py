"""T09: matching prototype on a tiny hand-built graph.

Lessons here are test data in the shape of docs/condition-kinds.md. Real lessons are
stored in FalkorDB and loaded from there (T14-T17).
"""
import pytest

from nodus.compiler import CompileError, compile_condition
from nodus.matcher import evaluate

# Antibody 1: "The trusted change, everywhere at once" (n = 5)
ANTIBODY_1 = {
    "id": "antibody-1",
    "completion": "A1.5",
    "conditions": [
        {"id": "A1.1", "kind": "attribute_equals", "start": "anchor",
         "property": "risk_class", "value": "routine"},
        {"id": "A1.2", "kind": "present", "start": "other:Plan",
         "path": [["FOLLOWS", "out"]],
         "target": {"label": "Procedure", "props": {"kind": "staged_rollout"}},
         "bind": "proc"},
        {"id": "A1.3", "kind": "absent", "start": "anchor",
         "path": [["FOLLOWS", "out"]], "target": {"role": "proc"}},
        {"id": "A1.4", "kind": "count_equals", "start": "anchor",
         "path": [["GATED_BY", "out"]], "target": {"label": "Check"},
         "n": 1, "all_targets": {"kind": "automated"}},
        {"id": "A1.5", "kind": "present", "start": "anchor",
         "path": [["HAS_STEP", "out"]],
         "target": {"label": "Step", "props": {"kind": "rollout", "scope": "all"}}},
    ],
}

# Antibody 2: "The warning that went nowhere" (n = 4)
ANTIBODY_2 = {
    "id": "antibody-2",
    "completion": "A2.4",
    "conditions": [
        {"id": "A2.1", "kind": "present", "start": "anchor",
         "path": [["TARGETS", "out"], ["ALERTS_TO", "out"]],
         "target": {"label": "Channel"}, "bind": "ch"},
        {"id": "A2.2", "kind": "attribute_equals", "start": "role:ch",
         "property": "kind", "value": "email_list"},
        {"id": "A2.3", "kind": "absent", "start": "role:ch",
         "path": [["WATCHES", "in"]],
         "target": {"label": "Person", "props": {"active": True}}},
        {"id": "A2.4", "kind": "present", "start": "anchor",
         "path": [["HAS_STEP", "out"]],
         "target": {"label": "Step", "props": {"kind": "rollout"}}},
    ],
}

# The hero: routine change, skips the staged procedure others follow, one automated
# gate, alerts to an email list only an ex-employee watches, NO rollout step yet.
HERO_WORLD = """
CREATE (hero:Plan {id:'hero', risk_class:'routine'}),
       (other:Plan {id:'other', risk_class:'standard'}),
       (pr:Procedure {id:'proc-staged', kind:'staged_rollout'}),
       (other)-[:FOLLOWS]->(pr),
       (hero)-[:GATED_BY]->(:Check {id:'chk-auto', kind:'automated'}),
       (hero)-[:TARGETS]->(:System {id:'sys-edge'})-[:ALERTS_TO]->(ch:Channel {id:'ch-mail', kind:'email_list'}),
       (:Person {id:'ex-employee', active:false})-[:WATCHES]->(ch),
       (hero)-[:HAS_STEP]->(:Step {id:'step-test', kind:'test', scope:'subset'})
"""


@pytest.fixture
def hero(graph):
    graph.query(HERO_WORLD)
    return graph


def holding(result):
    return [c.id for c in result.conditions if c.holds]


# 1. all conditions met -> k = n, "full"
def test_all_conditions_met_is_full(hero):
    hero.query("MATCH (p:Plan {id:'hero'}) "
               "CREATE (p)-[:HAS_STEP]->(:Step {id:'step-go', kind:'rollout', scope:'all'})")
    r = evaluate(hero, "hero", ANTIBODY_1)
    assert (r.k, r.n, r.status) == (5, 5, "full")


# 2. n-1 with the completion step pending -> "foresight"
def test_completion_pending_is_foresight(hero):
    r = evaluate(hero, "hero", ANTIBODY_1)
    assert (r.k, r.n, r.status) == (4, 5, "foresight")
    assert r.missing == ["A1.5"]


# 3. n-1 with a different condition missing -> "strong"
def test_other_condition_missing_is_strong(hero):
    hero.query("MATCH (p:Plan {id:'hero'}), (pr:Procedure {id:'proc-staged'}) "
               "CREATE (p)-[:FOLLOWS]->(pr), "
               "(p)-[:HAS_STEP]->(:Step {id:'step-go', kind:'rollout', scope:'all'})")
    r = evaluate(hero, "hero", ANTIBODY_1)
    assert (r.k, r.status, r.missing) == (4, "strong", ["A1.3"])


# 4a. binding trap: an unwatched email list exists, but on ANOTHER plan's system.
#     The hero's own channel is a watched pager. It must not borrow the other channel.
def test_binding_trap_uses_only_the_anchors_channel(graph):
    graph.query("""
    CREATE (hero:Plan {id:'hero'}),
           (hero)-[:TARGETS]->(:System {id:'sys-hero'})-[:ALERTS_TO]->(pg:Channel {id:'ch-pager', kind:'pager'}),
           (:Person {id:'oncall', active:true})-[:WATCHES]->(pg),
           (:Plan {id:'unrelated'})-[:TARGETS]->(:System {id:'sys-x'})
               -[:ALERTS_TO]->(:Channel {id:'ch-orphan', kind:'email_list'})
    """)
    r = evaluate(graph, "hero", ANTIBODY_2)
    assert r.bindings == {"ch": "ch-pager"}
    assert holding(r) == ["A2.1"]


# 4b. two real candidates for one role: keep the one giving the highest k
def test_two_candidates_keeps_highest_k(hero):
    hero.query("""
    MATCH (s:System {id:'sys-edge'})
    CREATE (s)-[:ALERTS_TO]->(pg:Channel {id:'ch-a-pager', kind:'pager'}),
           (:Person {id:'oncall', active:true})-[:WATCHES]->(pg)
    """)
    r = evaluate(hero, "hero", ANTIBODY_2)
    assert r.bindings == {"ch": "ch-mail"}
    assert (r.k, r.status) == (3, "foresight")


# 5. an absence condition holds when the relationship is missing...
def test_absence_holds_when_relationship_missing(hero):
    r = evaluate(hero, "hero", ANTIBODY_2)
    assert next(c for c in r.conditions if c.id == "A2.3").holds


# ...and stops holding once an active person watches the channel
def test_absence_fails_when_active_watcher_added(hero):
    hero.query("MATCH (ch:Channel {id:'ch-mail'}) "
               "CREATE (:Person {id:'sre', active:true})-[:WATCHES]->(ch)")
    r = evaluate(hero, "hero", ANTIBODY_2)
    assert not next(c for c in r.conditions if c.id == "A2.3").holds


# 6. a binder that finds nothing leaves its dependents "unbound", never true
def test_missing_binder_makes_dependents_unbound(graph):
    graph.query("CREATE (:Plan {id:'hero'})")
    r = evaluate(graph, "hero", ANTIBODY_2)
    states = {c.id: c.state for c in r.conditions}
    assert states == {"A2.1": "missing", "A2.2": "unbound",
                      "A2.3": "unbound", "A2.4": "missing"}
    assert r.k == 0


# 7. "only gate" counting is not fooled by parallel relationships (T06 finding)
def test_count_equals_counts_parallel_gates(hero):
    hero.query("MATCH (p:Plan {id:'hero'}), (c:Check {id:'chk-auto'}) "
               "CREATE (p)-[:GATED_BY]->(c)")
    r = evaluate(hero, "hero", ANTIBODY_1)
    assert not next(c for c in r.conditions if c.id == "A1.4").holds


# 8. the compiler refuses identifiers outside the graph model's whitelist
def test_compiler_rejects_unknown_relationship():
    bad = {"id": "X", "kind": "present", "start": "anchor",
           "path": [["DROP_EVERYTHING", "out"]], "target": {"label": "Plan"}}
    with pytest.raises(CompileError):
        compile_condition(bad, anchor="hero", bindings={})


# 9. values never appear in the query text; they travel as parameters
def test_values_are_parameters_not_text():
    cond = ANTIBODY_1["conditions"][0]
    cypher, params = compile_condition(cond, anchor="hero'; MATCH (n) DETACH DELETE n //",
                                       bindings={})
    assert "routine" not in cypher and "DELETE" not in cypher
    assert "routine" in params.values()


# 10. an anchor id that isn't in the graph gives k = 0, not a crash
def test_unknown_anchor_gives_zero(hero):
    r = evaluate(hero, "no-such-plan", ANTIBODY_1)
    assert (r.k, r.status) == (0, "partial")
