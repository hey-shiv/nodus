"""T17 / G3: the designed plans give exactly the designed results on the real world."""
import pytest

from nodus.watch import echoes, run
from scripts.setup_demo import build


@pytest.fixture
def world(graph):
    build(graph, approve_as="tester")
    return graph


@pytest.fixture
def table(world):
    return {(p, r.lesson_id): r for p, r in run(world)}


def kn(table, plan, lesson):
    r = table.get((plan, lesson))
    return (r.k, r.n, r.status) if r else None


def test_hero_is_one_step_from_three_failures(table):
    assert kn(table, "plan-hero", "antibody-1") == (4, 5, "foresight")
    assert kn(table, "plan-hero", "antibody-2") == (3, 4, "foresight")
    assert kn(table, "plan-hero", "internal-quiet-push") == (4, 5, "foresight")
    assert table[("plan-hero", "antibody-1")].missing == ["A1.5"]


def test_internal_echo_matches_the_companys_own_lesson(table):
    assert kn(table, "plan-maps", "internal-quiet-push") == (5, 5, "full")


def test_control_raises_nothing_despite_the_words(table):
    raised = echoes([(plan, r) for (plan, _), r in table.items()])
    assert [r.lesson_id for plan, r in raised if plan == "plan-sensor"] == []


def test_near_miss_is_lower_k_and_not_raised(table):
    assert kn(table, "plan-scanner", "antibody-1") == (3, 5, "partial")


def test_clean_plan_raises_nothing(table):
    assert all(r.status == "partial" for (p, _), r in table.items() if p == "plan-billing")


def test_past_plans_are_not_watched(table):
    assert not any(p in ("plan-e1", "plan-e2") or p.startswith("plan-bg") for p, _ in table)


def test_unapproved_lessons_never_match(graph):
    build(graph, approve_as=None)
    assert run(graph) == []
