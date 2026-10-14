"""Build the demo graph from scratch: the synthetic world + the three lessons.

Run:  .venv/bin/python scripts/setup_demo.py [--approve]
--approve records the builder's approval of the hand-authored lessons (otherwise
approve them on the app's Lessons page).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nodus.db import get_graph  # noqa: E402
from nodus.lessons import approve, load_lesson_file, load_sources, store  # noqa: E402
from nodus.loader import counts, load  # noqa: E402
from nodus.world import generate  # noqa: E402


def build(graph, approve_as=None):
    try:
        graph.delete()
    except Exception:
        pass
    load(graph, generate())
    sources = load_sources()
    for path in sorted(Path(__file__).resolve().parent.parent.glob("data/lessons/*.json")):
        lesson = load_lesson_file(path)
        store(graph, lesson, sources)
        if approve_as:
            approve(graph, lesson.id, approve_as)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--approve", action="store_true")
    args = ap.parse_args()
    g = get_graph()
    build(g, "Shivashant (builder)" if args.approve else None)
    nodes, rels = counts(g)
    print(f"graph '{g.name}': {sum(nodes.values())} nodes, {sum(rels.values())} relationships")
