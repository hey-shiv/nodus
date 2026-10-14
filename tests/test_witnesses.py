"""T21: witness routing follows B8's order exactly."""
import pytest

from nodus.witnesses import route, sources

BASE = """
CREATE (l:Lesson {id:'L', origin:'synthetic'}),
       (l)-[:LEARNED_FROM]->(e:Episode {id:'ep', title:'Old outage'}),
       (e)-[:INVOLVED]->(past:Plan {id:'past'}),
       (e)-[:DESCRIBED_IN]->(d:Document {id:'pm', title:'The post-mortem'}),
       (now:Plan {id:'now'})-[:TARGETS]->(s:System {id:'sys', name:'Core'})
"""


@pytest.fixture
def g(graph):
    graph.query(BASE)
    return graph


def add(g, cypher):
    g.query("MATCH (past:Plan {id:'past'}), (d:Document {id:'pm'}), (s:System {id:'sys'}) " + cypher)


def test_active_concern_raiser_is_chosen_first(g):
    add(g, "CREATE (:Person {id:'ann', name:'Ann', active:true})-[:RAISED]->"
           "(:Concern {summary:'wait', resolution:'overruled'})-[:ABOUT]->(past), "
           "(:Person {id:'bo', name:'Bo', active:true})-[:AUTHORED]->(d)")
    w = route(g, "L", "now")
    assert (w.person_id, w.rule) == ("ann", 1)


def test_inactive_concern_raiser_is_skipped(g):
    add(g, "CREATE (:Person {id:'ann', name:'Ann', active:false})-[:RAISED]->"
           "(:Concern {summary:'wait', resolution:'overruled'})-[:ABOUT]->(past), "
           "(:Person {id:'bo', name:'Bo', active:true})-[:AUTHORED]->(d)")
    assert route(g, "L", "now").person_id == "bo"


def test_accepted_concern_does_not_count(g):
    add(g, "CREATE (:Person {id:'ann', name:'Ann', active:true})-[:RAISED]->"
           "(:Concern {summary:'wait', resolution:'accepted'})-[:ABOUT]->(past)")
    assert route(g, "L", "now") is None


def test_postmortem_author_fallback(g):
    add(g, "CREATE (:Person {id:'bo', name:'Bo', active:true})-[:AUTHORED]->(d)")
    assert route(g, "L", "now").rule == 2


def test_system_owner_fallback(g):
    add(g, "CREATE (:Person {id:'cy', name:'Cy', active:true})-[:OWNS]->(s)")
    w = route(g, "L", "now")
    assert (w.person_id, w.rule) == ("cy", 3)


def test_none_available_is_honest(g):
    add(g, "CREATE (:Person {id:'cy', name:'Cy', active:false})-[:OWNS]->(s)")
    assert route(g, "L", "now") is None


def test_public_antibody_returns_sources_never_people(graph):
    graph.query("CREATE (l:Lesson {id:'A', origin:'public'})-[:LEARNED_FROM]->"
                "(:Document {id:'d1', title:'Post-mortem', url:'https://x', publisher:'Org'}), "
                "(:Plan {id:'now'})-[:TARGETS]->(:System {id:'s'})<-[:OWNS]-(:Person {id:'p', active:true})")
    assert route(graph, "A", "now") is None
    assert [s["id"] for s in sources(graph, "A")] == ["d1"]
