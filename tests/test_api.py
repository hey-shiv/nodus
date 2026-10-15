"""The website's API, end to end through HTTP (FastAPI TestClient), on throwaway graphs."""
import uuid

import pytest
from fastapi.testclient import TestClient

import nodus.sandbox as sandbox
from api.server import app
from nodus.db import get_db


@pytest.fixture(scope="module")
def client():
    db = get_db()
    old = sandbox.TEMPLATE
    sandbox.TEMPLATE = f"lab_tpl_{uuid.uuid4().hex[:8]}"
    before = set(db.list_graphs())
    yield TestClient(app)
    for name in set(db.list_graphs()) - before:            # template + sandboxes made here
        db.select_graph(name).delete()
    sandbox.TEMPLATE = old


@pytest.fixture
def sbx(client):
    return {"X-Nodus-Sandbox": client.post("/api/sandbox").json()["sandbox"]}


def test_no_sandbox_is_refused(client):
    assert client.get("/api/plans").status_code == 401
    assert client.get("/api/plans", headers={"X-Nodus-Sandbox": "sbx_1_nothere"}).status_code == 401


def test_plans_overview_matches_the_engine(client, sbx):
    data = client.get("/api/plans", headers=sbx).json()
    hero = next(p for p in data["plans"] if p["id"] == "plan-hero")
    levels = {x["lesson"]: x["level"] for x in hero["lessons"]}
    assert levels["antibody-1"] == "foresight" and data["one_step"] == 2
    assert hero["lessons"][0]["strip"].startswith("<svg")


def test_echo_returns_the_drawing_and_sources(client, sbx):
    e = client.get("/api/echo", params={"plan": "plan-hero", "lesson": "antibody-1"}, headers=sbx).json()
    assert (e["k"], e["n"], e["level"]) == (4, 5, "foresight") and e["completion_missing"]
    assert e["svg"].startswith("<svg") and "4 OF 5" in e["svg"]
    assert {s["publisher"] for s in e["sources"]} == {"Cloudflare", "CrowdStrike"}


def test_melody_is_wav(client, sbx):
    r = client.get("/api/melody", params={"plan": "plan-hero", "lesson": "antibody-1",
                                          "sbx": sbx["X-Nodus-Sandbox"]})
    assert r.status_code == 200 and r.headers["content-type"] == "audio/wav"
    assert r.content[:4] == b"RIFF"


def test_saving_the_completion_step_turns_foresight_full(client, sbx):
    body = {"follows_canary": False, "peer_review": False,
            "add_step": {"kind": "rollout", "scope": "all"}}
    raised = client.post("/api/plans/plan-hero", json=body, headers=sbx).json()["raised"]
    assert {r["lesson"]: r["level"] for r in raised}["antibody-1"] == "full"


def test_sandboxes_are_isolated(client, sbx):
    other = {"X-Nodus-Sandbox": client.post("/api/sandbox").json()["sandbox"]}
    client.post("/api/plans/plan-hero", headers=sbx, json={
        "follows_canary": True, "peer_review": True})
    mine = client.get("/api/echo", params={"plan": "plan-hero", "lesson": "antibody-1"}, headers=sbx).json()
    theirs = client.get("/api/echo", params={"plan": "plan-hero", "lesson": "antibody-1"}, headers=other).json()
    assert mine["k"] < theirs["k"] == 4


def test_inbox_and_answer(client, sbx):
    msgs = client.get("/api/inbox", params={"person": "p-lena"}, headers=sbx).json()
    eid = next(m["echo_id"] for m in msgs if m["lesson_id"] == "antibody-1")
    bad = client.post("/api/answer", headers=sbx, json={"echo_id": eid, "person": "Lena Brandt",
                                                        "outcome": "dismissed"})
    assert bad.status_code == 422                      # a dismissal needs a reason
    ok = client.post("/api/answer", headers=sbx, json={"echo_id": eid, "person": "Lena Brandt",
                                                       "outcome": "heeded"})
    assert ok.json() == {"ok": True}
    track = next(l for l in client.get("/api/lessons", headers=sbx).json() if l["id"] == "antibody-1")
    assert track["track"]["heeded"] == 1


def test_bad_ids_are_rejected(client, sbx):
    assert client.get("/api/echo", params={"plan": "x' OR 1=1", "lesson": "a"}, headers=sbx).status_code == 400
    assert client.post("/api/plans/plan-hero", headers=sbx, json={
        "follows_canary": False, "peer_review": False,
        "add_step": {"kind": "DROP", "scope": "all"}}).status_code == 422


def test_ag_ui_endpoint_streams_events(client, sbx):
    run = {"threadId": "t1", "runId": "r1", "state": {"plan_id": "plan-hero"}, "messages": [],
           "tools": [], "context": [], "forwardedProps": {}}
    with client.stream("POST", "/api/agent", json=run, headers=sbx) as r:
        assert r.headers["content-type"].startswith("text/event-stream")
        body = "".join(r.iter_text())
    frames = [f for f in body.split("\n\n") if f.startswith("data: ")]
    assert '"RUN_STARTED"' in frames[0] and '"RUN_FINISHED"' in frames[-1]
    assert any('"TOOL_CALL_START"' in f for f in frames)
