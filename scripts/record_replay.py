"""Record real API responses so the website can replay them when the live database is offline.

Needs a local FalkorDB (docker compose up -d). Run from the repo root:

    .venv/bin/python -m scripts.record_replay

Writes web/public/replay/: fresh.json (every read on an untouched sandbox), plans/<plan>.json
(one entry per plan setup reachable in a single save), and r/<hash>.json|txt|wav bodies,
stored once by content. web/lib/api.ts reads these when /api/health fails.
"""
import hashlib
import itertools
import json
import os
import shutil
from pathlib import Path

os.environ.setdefault("NODUS_MAX_SANDBOXES", "8")

from fastapi.testclient import TestClient  # noqa: E402

import api.server  # noqa: E402
from api.server import app  # noqa: E402
from nodus.db import get_db  # noqa: E402

_db = get_db()
api.server.get_db = lambda: _db   # one connection pool; a new one per request runs out of local ports

OUT = Path("web/public/replay")
KINDS = ["canary", "test", "review", "rollout"]
SCOPES = ["subset", "all"]
c = TestClient(app)


def store(body: bytes, ext: str) -> str:
    h = hashlib.sha1(body).hexdigest()[:16]
    p = OUT / "r" / f"{h}.{ext}"
    if not p.exists():
        p.write_bytes(body)
    return f"{h}.{ext}"


def get(path, sbx):
    r = c.get(path, headers={"X-Nodus-Sandbox": sbx})
    if r.status_code != 200:
        return {"e": r.status_code, "d": r.json().get("detail", "")}
    return store(r.content, "json")


def agent(plan, sbx):
    r = c.post("/api/agent", headers={"X-Nodus-Sandbox": sbx}, json={
        "threadId": f"plan-{plan}", "runId": "recorded", "state": {"plan_id": plan},
        "messages": [], "tools": [], "context": [], "forwardedProps": {}})
    return store(r.content, "txt")


def config(detail):
    steps = sorted(f"{s['kind']}-{s['scope']}" for s in detail["steps"])
    return f"f{int(detail['follows_canary'])}r{int(detail['peer_review'])}:{','.join(steps)}"


def new_sandbox():
    return c.post("/api/sandbox").json()["sandbox"]


def plan_reads(sbx, plan, lessons, people):
    """Everything a save to `plan` can change."""
    reads = {"/api/plans": get("/api/plans", sbx), f"/api/plans/{plan}": get(f"/api/plans/{plan}", sbx),
             "/api/compare": get("/api/compare", sbx), "/api/lessons": get("/api/lessons", sbx),
             f"agent:{plan}": agent(plan, sbx)}
    for les in lessons:
        reads[f"/api/echo?plan={plan}&lesson={les}"] = get(f"/api/echo?plan={plan}&lesson={les}", sbx)
    for p in people:
        reads[f"/api/inbox?person={p}"] = get(f"/api/inbox?person={p}", sbx)
    return reads


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "r").mkdir(parents=True)
    (OUT / "plans").mkdir()

    sbx = new_sandbox()
    h = {"X-Nodus-Sandbox": sbx}
    overview = c.get("/api/plans", headers=h).json()
    plans = [p["id"] for p in overview["plans"]]
    lessons = [l["id"] for l in c.get("/api/lessons", headers=h).json()]
    people = [p["id"] for p in c.get("/api/people", headers=h).json()]

    fresh = {"/api/people": get("/api/people", sbx)}
    for plan in plans:
        fresh.update(plan_reads(sbx, plan, lessons, people))
    melody = {}
    for p in overview["plans"]:
        for row in p["lessons"]:
            if not row["warning"]:
                continue
            echo = c.get(f"/api/echo?plan={p['id']}&lesson={row['lesson']}", headers=h).json()
            for resolve in ([False, True] if echo["completion_missing"] else [False]):
                wav = c.get(f"/api/melody?plan={p['id']}&lesson={row['lesson']}&resolve={str(resolve).lower()}&sbx={sbx}")
                melody[f"{p['id']}|{row['lesson']}|{str(resolve).lower()}"] = store(wav.content, "wav")
    fresh_details = {plan: c.get(f"/api/plans/{plan}", headers=h).json() for plan in plans}
    (OUT / "fresh.json").write_text(json.dumps({
        "reads": fresh, "melody": melody,
        "configs": {plan: config(d) for plan, d in fresh_details.items()}}, separators=(",", ":")))

    for plan in plans:
        base = fresh_details[plan]
        states = {}
        adds = [None] + [{"kind": k, "scope": s} for k in KINDS for s in SCOPES]
        removals = [list(r) for n in range(len(base["steps"]) + 1)
                    for r in itertools.combinations([s["id"] for s in base["steps"]], n)]
        for follows, review, add, remove in itertools.product([False, True], [False, True], adds, removals):
            sbx = new_sandbox()
            r = c.post(f"/api/plans/{plan}", headers={"X-Nodus-Sandbox": sbx}, json={
                "follows_canary": follows, "peer_review": review, "add_step": add, "remove_steps": remove})
            cfg = config(c.get(f"/api/plans/{plan}", headers={"X-Nodus-Sandbox": sbx}).json())
            if cfg in states:
                continue
            states[cfg] = {"save": store(r.content, "json"), "reads": plan_reads(sbx, plan, lessons, people)}
        (OUT / "plans" / f"{plan}.json").write_text(json.dumps(states, separators=(",", ":")))
        print(plan, len(states), "setups")

    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"{len(list((OUT / 'r').iterdir()))} bodies, {size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
