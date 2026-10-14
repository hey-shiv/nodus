"""Whom to invite about an echo (plan B8). Rules applied strictly in order.

1. An active person who raised a concern in the original episode that was overruled or left open.
2. An active author of the original episode's post-mortem.
3. An active owner of a system the current plan targets.
4. Otherwise nobody ("no witness available" is an honest answer).
Public antibodies never return people: their witnesses are their source documents.
Graph distance is never used as "expertise", and witnesses are never scored or ranked.
"""
from dataclasses import dataclass

from nodus.db import read


@dataclass
class Witness:
    person_id: str
    name: str
    rule: int
    reason: str


def sources(graph, lesson_id):
    return [{"id": r[0], "title": r[1], "url": r[2], "publisher": r[3]} for r in read(
        graph, "MATCH (l:Lesson {id: $id})-[x:LEARNED_FROM]->(d:Document) "
               "RETURN d.id, d.title, d.url, d.publisher ORDER BY d.id", {"id": lesson_id})]


def route(graph, lesson_id, plan_id):
    """Return a Witness, or None. For public lessons, use sources() instead."""
    origin = read(graph, "MATCH (l:Lesson {id: $id}) RETURN l.origin", {"id": lesson_id})
    if not origin or origin[0][0] == "public":
        return None
    rule1 = read(graph,
        "MATCH (l:Lesson {id: $id})-[a:LEARNED_FROM]->(e:Episode)-[b:INVOLVED]->(past:Plan)"
        "<-[c:ABOUT]-(con:Concern)<-[d:RAISED]-(p:Person {active: true}) "
        "WHERE con.resolution IN ['overruled', 'open'] "
        "RETURN DISTINCT p.id, p.name, con.summary, e.title ORDER BY p.id", {"id": lesson_id})
    if rule1:
        pid, name, concern, episode = rule1[0]
        return Witness(pid, name, 1, f'raised "{concern}" during "{episode}"')
    rule2 = read(graph,
        "MATCH (l:Lesson {id: $id})-[a:LEARNED_FROM]->(e:Episode)-[b:DESCRIBED_IN]->(doc:Document)"
        "<-[c:AUTHORED]-(p:Person {active: true}) "
        "RETURN DISTINCT p.id, p.name, doc.title ORDER BY p.id", {"id": lesson_id})
    if rule2:
        pid, name, doc = rule2[0]
        return Witness(pid, name, 2, f'wrote "{doc}"')
    rule3 = read(graph,
        "MATCH (pl:Plan {id: $plan})-[a:TARGETS]->(s:System)<-[b:OWNS]-(p:Person {active: true}) "
        "RETURN DISTINCT p.id, p.name, s.name ORDER BY p.id", {"plan": plan_id})
    if rule3:
        pid, name, system = rule3[0]
        return Witness(pid, name, 3, f"owns {system}, which this plan changes")
    return None
