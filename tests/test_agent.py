"""T20, T22, T23: the agent loop on the demo world, and its memory."""
import pytest

from nodus.agent import acknowledge, echo_id, inbox, on_plan_saved, track_record
from nodus.db import read
from scripts.setup_demo import build


@pytest.fixture
def world(graph):
    build(graph, approve_as="tester")
    return graph


def by_lesson(report):
    return {r["lesson_id"]: r for r in report}


def test_hero_raises_three_foresight_echoes(world):
    report = by_lesson(on_plan_saved(world, "plan-hero", now=1000))
    assert {k: r["level"] for k, r in report.items()} == {
        "antibody-1": "foresight", "antibody-2": "foresight", "internal-quiet-push": "foresight"}


def test_internal_echo_invites_the_person_who_warned(world):
    r = by_lesson(on_plan_saved(world, "plan-hero"))["internal-quiet-push"]
    assert r["witness"].name == "Asha Rao" and r["witness"].rule == 1
    assert "Asha Rao" in r["headsup"]
    assert "every depot at once" in r["headsup"]


def test_public_echo_cites_sources_not_people(world):
    r = by_lesson(on_plan_saved(world, "plan-hero"))["antibody-1"]
    assert r["witness"] is None
    assert {s["publisher"] for s in r["sources"]} == {"Cloudflare", "CrowdStrike"}


def test_silence_uses_recorded_graph_wording(world):
    r = by_lesson(on_plan_saved(world, "plan-hero"))["antibody-2"]
    assert any("Not recorded in the company graph" in s and "tariff-errors@ list" in s
               for s in r["silences"])
    assert any("active owner" in s for s in r["silences"])
    assert not any("forgot" in s.lower() for s in r["silences"])


def test_control_and_clean_raise_nothing(world):
    assert on_plan_saved(world, "plan-sensor") == []
    assert on_plan_saved(world, "plan-billing") == []


def test_saving_again_does_not_duplicate_echoes(world):
    on_plan_saved(world, "plan-hero", now=1000)
    on_plan_saved(world, "plan-hero", now=2000)
    rows = read(world, "MATCH (e:Echo) RETURN count(e), max(e.times_seen)")
    assert rows == [[3, 2]]


def test_taking_the_completion_step_turns_foresight_into_full(world):
    on_plan_saved(world, "plan-hero")
    world.query("MATCH (p:Plan {id:'plan-hero'}) CREATE (p)-[:HAS_STEP]->"
                "(:Step {id:'plan-hero-s9', kind:'rollout', scope:'all', at:1792800000})")
    report = by_lesson(on_plan_saved(world, "plan-hero"))
    assert report["antibody-1"]["level"] == "full"


def test_fixing_the_plan_clears_the_echo(world):
    on_plan_saved(world, "plan-hero")
    world.query("MATCH (p:Plan {id:'plan-hero'}), (c:Procedure {id:'proc-canary'}) "
                "CREATE (p)-[:FOLLOWS]->(c)")
    on_plan_saved(world, "plan-hero")
    status = read(world, "MATCH (e:Echo {id: $id}) RETURN e.status",
                  {"id": echo_id("internal-quiet-push", "plan-hero")})
    assert status == [["cleared"]]


def test_heeded_outcome_updates_track_record(world):
    on_plan_saved(world, "plan-hero")
    acknowledge(world, echo_id("antibody-1", "plan-hero"), "Lena Brandt", "heeded")
    rec = track_record(world, "antibody-1")
    assert (rec["raised"], rec["heeded"], rec["open"]) == (1, 1, 0)


def test_dismissal_needs_a_reason(world):
    on_plan_saved(world, "plan-hero")
    with pytest.raises(ValueError, match="reason"):
        acknowledge(world, echo_id("antibody-2", "plan-hero"), "Lena Brandt", "dismissed")
    acknowledge(world, echo_id("antibody-2", "plan-hero"), "Lena Brandt", "dismissed",
                reason="tariff errors are also checked by finance daily")
    assert track_record(world, "antibody-2")["reasons"] == [
        "tariff errors are also checked by finance daily"]


def test_outcome_survives_a_later_save(world):
    on_plan_saved(world, "plan-hero")
    acknowledge(world, echo_id("antibody-1", "plan-hero"), "Lena Brandt", "heeded")
    on_plan_saved(world, "plan-hero")
    rows = [r for r in inbox(world) if r[0] == echo_id("antibody-1", "plan-hero")]
    assert rows[0][9:11] == ["acknowledged", "heeded"]
