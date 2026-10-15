"""The agent loop as an AG-UI event stream (github.com/ag-ui-protocol/ag-ui, MIT).

AG-UI is an open protocol for showing what an agent does: run and step boundaries, tool calls
with arguments and results, shared state, and messages. NODUS maps its loop onto it:

  STEP observe   STATE_SNAPSHOT  the plan's recorded structure
  STEP match     TOOL_CALL_*     one "check_condition" call per graph query actually run,
                                 args = the condition and bound roles, result = holds + ids
  STEP decide    STATE_DELTA     k, n, level and missing conditions per lesson (JSON Patch)
  STEP act       TEXT_MESSAGE_*  the template-filled heads-up for each warning-level echo
  STEP remember  STATE_DELTA     the stored Echo record ids

Any AG-UI client can consume it. Nothing here changes a result: the loop runs exactly as in
nodus.agent.on_plan_saved, with an observer attached.
"""
import json
import uuid

from ag_ui.core import (EventType, RunErrorEvent, RunFinishedEvent, RunStartedEvent,
                        StateDeltaEvent, StateSnapshotEvent, StepFinishedEvent,
                        StepStartedEvent, TextMessageContentEvent, TextMessageEndEvent,
                        TextMessageStartEvent, ToolCallArgsEvent, ToolCallEndEvent,
                        ToolCallResultEvent, ToolCallStartEvent)
from ag_ui.encoder import EventEncoder

from nodus.agent import on_plan_saved
from nodus.db import read
from nodus.plans import plan_facts

_ENCODER = EventEncoder()


def encode(event):
    """One event as a Server-Sent Events frame: 'data: {...}\\n\\n'."""
    return _ENCODER.encode(event)


class _Trace:
    def __init__(self):
        self.calls, self.decisions = [], []

    def condition(self, lesson, cond, bindings, result):
        self.calls.append((lesson["id"], cond, bindings, result))

    def decision(self, lesson, result, lvl):
        self.decisions.append((lesson["id"], result, lvl))


def _step(name, events):
    yield StepStartedEvent(type=EventType.STEP_STARTED, step_name=name)
    yield from events
    yield StepFinishedEvent(type=EventType.STEP_FINISHED, step_name=name)


def _tool_calls(trace, plan_id):
    for i, (lesson_id, cond, bindings, result) in enumerate(trace.calls, start=1):
        call_id = f"call-{i}"
        args = {"lesson": lesson_id, "condition": cond["id"], "kind": cond["kind"],
                "anchor": plan_id, "bindings": bindings}
        yield ToolCallStartEvent(type=EventType.TOOL_CALL_START, tool_call_id=call_id,
                                 tool_call_name="check_condition")
        yield ToolCallArgsEvent(type=EventType.TOOL_CALL_ARGS, tool_call_id=call_id,
                                delta=json.dumps(args))
        yield ToolCallEndEvent(type=EventType.TOOL_CALL_END, tool_call_id=call_id)
        yield ToolCallResultEvent(type=EventType.TOOL_CALL_RESULT, message_id=f"result-{i}",
                                  tool_call_id=call_id, content=json.dumps(
                                      {"holds": result.holds, "state": result.state,
                                       "ids": list(result.ids)}))


def _decisions(trace):
    ops = []
    for lesson_id, result, lvl in trace.decisions:
        ops += [{"op": "add", "path": f"/echoes/{lesson_id}", "value": {}},
                {"op": "add", "path": f"/echoes/{lesson_id}/k", "value": result.k},
                {"op": "add", "path": f"/echoes/{lesson_id}/n", "value": result.n},
                {"op": "add", "path": f"/echoes/{lesson_id}/level", "value": lvl},
                {"op": "add", "path": f"/echoes/{lesson_id}/missing", "value": result.missing}]
    yield StateDeltaEvent(type=EventType.STATE_DELTA, delta=ops)


def _messages(report):
    for r in report:
        mid = f"msg-{r['lesson_id']}"
        text = r["headsup"] + "".join("\n" + s for s in r["silences"])
        yield TextMessageStartEvent(type=EventType.TEXT_MESSAGE_START, message_id=mid,
                                    role="assistant")
        yield TextMessageContentEvent(type=EventType.TEXT_MESSAGE_CONTENT, message_id=mid,
                                      delta=text)
        yield TextMessageEndEvent(type=EventType.TEXT_MESSAGE_END, message_id=mid)


def _memory(report):
    ops = [{"op": "add", "path": f"/echoes/{r['lesson_id']}/echo_id", "value": r["echo_id"]}
           for r in report]
    yield StateDeltaEvent(type=EventType.STATE_DELTA, delta=ops)


def run_events(graph, plan_id, thread_id=None, run_id=None):
    """Run the agent loop on one plan and yield it as AG-UI events, in order."""
    thread_id, run_id = thread_id or f"thread-{plan_id}", run_id or uuid.uuid4().hex[:12]
    yield RunStartedEvent(type=EventType.RUN_STARTED, thread_id=thread_id, run_id=run_id)
    plan = read(graph, "MATCH (p:Plan {id: $id}) RETURN p.id, p.title, p.risk_class",
                {"id": plan_id})
    if not plan:
        yield RunErrorEvent(type=EventType.RUN_ERROR, message=f"no plan with id {plan_id!r}")
        return
    facts = plan_facts(graph, plan_id)
    snapshot = {"plan": {"id": plan[0][0], "title": plan[0][1], "risk_class": plan[0][2],
                         "steps": [{"kind": k, "scope": s} for _, k, s, _ in facts["steps"]],
                         "gates": [{"id": i, "kind": k} for i, _, k in facts["gates"]],
                         "follows": [i for i, _ in facts["follows"]]},
                "echoes": {}}
    trace = _Trace()
    report = on_plan_saved(graph, plan_id, trace=trace)                 # the real loop
    yield from _step("observe", [StateSnapshotEvent(type=EventType.STATE_SNAPSHOT,
                                                    snapshot=snapshot)])
    yield from _step("match", _tool_calls(trace, plan_id))
    yield from _step("decide", _decisions(trace))
    yield from _step("act", _messages(report))
    yield from _step("remember", _memory(report))
    yield RunFinishedEvent(type=EventType.RUN_FINISHED, thread_id=thread_id, run_id=run_id)
