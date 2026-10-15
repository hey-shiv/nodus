"""AG-UI: the agent loop streamed as standard AG-UI events (github.com/ag-ui-protocol/ag-ui)."""
import json

import pytest
from ag_ui.core import EventType

from nodus.agui import encode, run_events
from scripts.setup_demo import build


@pytest.fixture
def world(graph):
    build(graph, approve_as="tester")
    return graph


def types(events):
    return [e.type for e in events]


def test_stream_is_a_well_formed_ag_ui_run(world):
    ev = list(run_events(world, "plan-hero", thread_id="t1", run_id="r1"))
    assert ev[0].type == EventType.RUN_STARTED and ev[-1].type == EventType.RUN_FINISHED
    assert ev[0].thread_id == "t1" and ev[-1].run_id == "r1"
    starts = [e.tool_call_id for e in ev if e.type == EventType.TOOL_CALL_START]
    ends = [e.tool_call_id for e in ev if e.type == EventType.TOOL_CALL_END]
    results = [e.tool_call_id for e in ev if e.type == EventType.TOOL_CALL_RESULT]
    assert starts == ends == results and len(set(starts)) == len(starts)
    steps = [e.step_name for e in ev if e.type == EventType.STEP_STARTED]
    assert steps == ["observe", "match", "decide", "act", "remember"]


def test_every_condition_is_a_tool_call_with_its_real_result(world):
    ev = list(run_events(world, "plan-hero"))
    calls = {e.tool_call_id: e for e in ev if e.type == EventType.TOOL_CALL_START}
    args = {e.tool_call_id: json.loads(e.delta) for e in ev if e.type == EventType.TOOL_CALL_ARGS}
    res = {e.tool_call_id: json.loads(e.content) for e in ev if e.type == EventType.TOOL_CALL_RESULT}
    a15 = next(i for i, a in args.items() if a["condition"] == "A1.5")
    assert calls[a15].tool_call_name == "check_condition"
    assert res[a15]["holds"] is False                                  # the completion step
    a13 = next(i for i, a in args.items() if a["condition"] == "A1.3")
    assert args[a13]["kind"] == "absent" and res[a13]["holds"] is True
    assert args[a13]["bindings"] == {"proc": "proc-canary"}             # bound roles travel along


def test_decision_and_heads_up_are_streamed(world):
    ev = list(run_events(world, "plan-hero"))
    snap = next(e for e in ev if e.type == EventType.STATE_SNAPSHOT)
    assert snap.snapshot["plan"]["id"] == "plan-hero"
    deltas = [op for e in ev if e.type == EventType.STATE_DELTA for op in e.delta]
    levels = {op.path: op.value for op in deltas if op.path.endswith("/level")}   # typed JSON Patch ops
    assert levels["/echoes/antibody-1/level"] == "foresight"
    text = "".join(e.delta for e in ev if e.type == EventType.TEXT_MESSAGE_CONTENT)
    assert "every target at once" in text.lower() and "Asha Rao" in text


def test_quiet_plan_streams_no_heads_up(world):
    ev = list(run_events(world, "plan-sensor"))
    assert EventType.TEXT_MESSAGE_START not in types(ev)
    assert ev[-1].type == EventType.RUN_FINISHED


def test_unknown_plan_is_a_run_error(world):
    ev = list(run_events(world, "no-such-plan"))
    assert ev[-1].type == EventType.RUN_ERROR


def test_encoded_as_server_sent_events(world):
    first = encode(next(iter(run_events(world, "plan-hero", thread_id="t", run_id="r"))))
    assert first.startswith("data: ") and '"type":"RUN_STARTED"' in first and first.endswith("\n\n")
