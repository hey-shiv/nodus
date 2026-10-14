"""T12: loading is idempotent and matches the generator's own counts (G2)."""
from collections import Counter

from nodus.loader import counts, load
from nodus.world import generate


def expected(world):
    return (dict(Counter(n["label"] for n in world["nodes"])),
            dict(Counter(r["type"] for r in world["rels"])))


def test_load_matches_hand_count(graph):
    world = generate()
    load(graph, world)
    assert counts(graph) == expected(world)


def test_loading_twice_changes_nothing(graph):
    world = generate()
    load(graph, world)
    first = counts(graph)
    load(graph, world)
    assert counts(graph) == first
