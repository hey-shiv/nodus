"""T11: the synthetic world generator."""
import re
from collections import Counter

from nodus.world import generate

# Distinctive terms from the public post-mortems behind the antibodies (T16).
PUBLIC_KEY_TERMS = {
    "rollout", "staged", "global", "globally", "regex", "regular", "expression", "waf",
    "rule", "sop", "cpu", "content", "update", "channel", "sensor", "template", "validator",
    "validation", "crash", "router", "orders", "flag", "emails", "backup", "backups",
    "replication", "database", "snapshot", "snapshots", "capacity", "playbook", "subsystem",
}


def plan(world, id_):
    return next(n for n in world["nodes"] if n["id"] == id_)


def test_same_seed_same_world():
    assert generate(seed=7) == generate(seed=7)


def test_different_seed_changes_only_background():
    a, b = generate(seed=7), generate(seed=8)
    assert a != b
    core = lambda w: [n for n in w["nodes"] if not n["id"].startswith("plan-bg")
                      and not n["id"].startswith("plan-bg")]
    designed = {"plan-hero", "plan-maps", "plan-sensor", "plan-scanner", "plan-billing"}
    assert {n["id"] for n in core(a)} >= designed
    assert [plan(a, p) for p in designed] == [plan(b, p) for p in designed]


def test_every_node_is_synthetic_with_a_source():
    for n in generate()["nodes"]:
        assert n["props"]["origin"] == "synthetic"
        assert n["props"]["source"]


def test_ids_are_unique_and_rels_point_at_real_nodes():
    w = generate()
    ids = [n["id"] for n in w["nodes"]]
    assert len(ids) == len(set(ids))
    for r in w["rels"]:
        assert r["from"] in ids and r["to"] in ids


def test_hero_shares_no_key_terms_with_public_postmortems():
    hero = plan(generate(), "plan-hero")["props"]
    words = set(re.findall(r"[a-z]+", (hero["title"] + " " + hero["summary"]).lower()))
    assert words & PUBLIC_KEY_TERMS == set()


def test_control_does_share_key_terms():
    ctrl = plan(generate(), "plan-sensor")["props"]
    words = set(re.findall(r"[a-z]+", (ctrl["title"] + " " + ctrl["summary"]).lower()))
    assert len(words & PUBLIC_KEY_TERMS) >= 5


def test_most_changes_follow_the_staged_procedure():
    w = generate()
    followers = Counter(r["from"] for r in w["rels"]
                        if r["type"] == "FOLLOWS" and r["to"] == "proc-canary")
    assert len(followers) >= 10
