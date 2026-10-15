"""NODUS web API (FastAPI). Deployed on Vercel as a Python service under /api.

Every request after POST /api/sandbox carries the visitor's sandbox id in the
X-Nodus-Sandbox header; all reads and writes go to that private graph copy.
"""
import re
import time
import uuid

from ag_ui.core import RunAgentInput
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from nodus import sandbox, web
from nodus.agui import encode, run_events
from nodus.db import get_db

app = FastAPI(title="NODUS API", docs_url="/api/docs", openapi_url="/api/openapi.json")
_ID = re.compile(r"^[a-z0-9-]{1,40}$")
_ECHO = re.compile(r"^echo:[a-z0-9-]{1,40}:[a-z0-9-]{1,40}$")


def _graph(sbx):
    db = get_db()
    if not sandbox.is_valid(db, sbx):
        raise HTTPException(401, "No sandbox, or it expired. Start a new one with POST /api/sandbox.")
    return db.select_graph(sbx)


def _id(value, what="id"):
    if not value or not _ID.match(value):
        raise HTTPException(400, f"invalid {what}")
    return value


@app.get("/api/health")
def health():
    # db_ms: one database round trip, so a slow site can be told apart from a far-away database.
    db = get_db()
    db.connection.ping()
    t = time.perf_counter()
    db.connection.ping()
    return {"ok": True, "db_ms": round((time.perf_counter() - t) * 1000, 1)}


@app.post("/api/sandbox")
def new_sandbox():
    return {"sandbox": sandbox.create(get_db())}


@app.get("/api/plans")
def plans(x_nodus_sandbox: str = Header(None)):
    return web.plans_overview(_graph(x_nodus_sandbox))


@app.get("/api/plans/{plan_id}")
def plan(plan_id: str, x_nodus_sandbox: str = Header(None)):
    return web.plan_detail(_graph(x_nodus_sandbox), _id(plan_id, "plan"))


class StepIn(BaseModel):
    kind: str = Field(pattern="^(canary|test|review|rollout)$")
    scope: str = Field(pattern="^(subset|all)$")


class SaveIn(BaseModel):
    follows_canary: bool
    peer_review: bool
    add_step: StepIn | None = None
    remove_steps: list[str] = []


@app.post("/api/plans/{plan_id}")
def save(plan_id: str, body: SaveIn, x_nodus_sandbox: str = Header(None)):
    g = _graph(x_nodus_sandbox)
    for sid in body.remove_steps:
        _id(sid, "step")
    return {"raised": web.save_plan(g, _id(plan_id, "plan"), body.follows_canary, body.peer_review,
                                    body.add_step and body.add_step.model_dump(), body.remove_steps)}


@app.get("/api/echo")
def echo(plan: str, lesson: str, x_nodus_sandbox: str = Header(None)):
    try:
        return web.echo(_graph(x_nodus_sandbox), _id(plan, "plan"), _id(lesson, "lesson"))
    except (KeyError, StopIteration):
        raise HTTPException(404, "no such plan or approved lesson")


@app.get("/api/melody")
def melody(plan: str, lesson: str, resolve: bool = False, sbx: str = ""):
    # <audio src> can't send headers, so the sandbox comes as a query parameter here.
    wav = web.melody(_graph(sbx), _id(plan, "plan"), _id(lesson, "lesson"), resolve)
    return Response(wav, media_type="audio/wav")


@app.get("/api/people")
def people(x_nodus_sandbox: str = Header(None)):
    return web.people_list(_graph(x_nodus_sandbox))


@app.get("/api/inbox")
def inbox(person: str, x_nodus_sandbox: str = Header(None)):
    return web.inbox(_graph(x_nodus_sandbox), _id(person, "person"))


class AnswerIn(BaseModel):
    echo_id: str
    person: str = Field(min_length=1, max_length=80)
    outcome: str = Field(pattern="^(heeded|dismissed|escalated)$")
    reason: str = Field("", max_length=400)


@app.post("/api/answer")
def answer(body: AnswerIn, x_nodus_sandbox: str = Header(None)):
    if not _ECHO.match(body.echo_id):
        raise HTTPException(400, "invalid echo id")
    try:
        web.record_answer(_graph(x_nodus_sandbox), body.echo_id, body.person, body.outcome, body.reason)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"ok": True}


@app.get("/api/lessons")
def lessons(x_nodus_sandbox: str = Header(None)):
    return web.lessons_view(_graph(x_nodus_sandbox))


class DecisionIn(BaseModel):
    approve: bool
    by: str = Field(min_length=1, max_length=80)


@app.post("/api/lessons/{lesson_id}")
def decide(lesson_id: str, body: DecisionIn, x_nodus_sandbox: str = Header(None)):
    web.set_lesson_status(_graph(x_nodus_sandbox), _id(lesson_id, "lesson"), body.approve, body.by)
    return {"ok": True}


@app.get("/api/compare")
def compare(x_nodus_sandbox: str = Header(None)):
    return web.compare(_graph(x_nodus_sandbox))


@app.post("/api/agent")
async def agent(request: Request, x_nodus_sandbox: str = Header(None)):
    """AG-UI endpoint: POST a RunAgentInput with state {"plan_id": ...}; get an SSE event stream."""
    g = _graph(x_nodus_sandbox)
    run = RunAgentInput.model_validate(await request.json())
    plan_id = _id((run.state or {}).get("plan_id"), "plan")

    def stream():
        for event in run_events(g, plan_id, run.thread_id, run.run_id or uuid.uuid4().hex[:12]):
            yield encode(event)

    return StreamingResponse(stream(), media_type="text/event-stream")
