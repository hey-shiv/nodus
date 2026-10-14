"""Laya integration: suggestions never change a match until a person confirms them.

Uses a fake predictor shaped like laya's Router.predict result; no model is loaded.
"""
import pytest

from nodus.agent import acknowledge, echo_id, on_plan_saved, track_record
from nodus.lessons import active_lessons
from nodus.matcher import evaluate
from nodus.suggest import (categorise_reason, confirm_role, store_suggestions, suggest_roles,
                           suggestions_for)
from scripts.setup_demo import build


def fake(answers):
    """Return a predict() that answers each question id with a fixed label."""
    def predict(state, questions):
        (qid,) = questions
        return {"answers": {qid: {"choice": answers[qid], "confidence": 0.9}},
                "routing": {"model": "fake"}}
    return predict


@pytest.fixture
def world(graph):
    build(graph, approve_as="tester")
    return graph


def a1_k(graph, plan):
    les = next(l for l in active_lessons(graph) if l["id"] == "antibody-1")
    return evaluate(graph, plan, les).k


def test_suggest_roles_reads_router_shaped_answers():
    s = suggest_roles("Weekly tariff refresh", fake({"risk_class": "routine",
                                                     "change_type": "config_change"}))
    assert s == {"risk_class": ("routine", 0.9), "change_type": ("config_change", 0.9)}


def test_a_suggestion_alone_never_changes_the_match(world):
    before = a1_k(world, "plan-sensor")                       # recorded: standard
    store_suggestions(world, "plan-sensor", {"risk_class": ("routine", 0.95),
                                             "change_type": ("config_change", 0.9)})
    assert a1_k(world, "plan-sensor") == before
    assert suggestions_for(world, "plan-sensor")["risk_class"] == {
        "recorded": "standard", "suggested": "routine", "confidence": 0.95}


def test_confirming_a_suggestion_does_change_the_match(world):
    before = a1_k(world, "plan-sensor")
    confirm_role(world, "plan-sensor", "risk_class", "routine", "Kai Tanaka")
    assert a1_k(world, "plan-sensor") == before + 1           # A1.1 now holds


def test_only_vocabulary_values_are_accepted(world):
    with pytest.raises(ValueError):
        store_suggestions(world, "plan-hero", {"risk_class": ("dangerous", 0.9)})
    with pytest.raises(ValueError):
        confirm_role(world, "plan-hero", "owner", "someone", "x")


def test_dismissal_reasons_are_categorised_into_the_track_record(world):
    on_plan_saved(world, "plan-hero")
    acknowledge(world, echo_id("antibody-2", "plan-hero"), "Lena Brandt", "dismissed",
                reason="finance checks the tariff errors every morning",
                categorise=lambda r: categorise_reason(r, fake({"reason": "mitigated_elsewhere"})))
    assert track_record(world, "antibody-2")["reason_categories"] == {"mitigated_elsewhere": 1}


def test_heeded_outcomes_are_not_categorised(world):
    on_plan_saved(world, "plan-hero")
    called = []
    acknowledge(world, echo_id("antibody-1", "plan-hero"), "Lena Brandt", "heeded",
                categorise=lambda r: called.append(r) or ("other", 0.5))
    assert called == []
