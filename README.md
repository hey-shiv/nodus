# NODUS

> Learn from mistakes you never made.

**Work in progress** (Graph Hacks, Oct 15–18, 2026, Track 03: Company Brain).

NODUS flags when a new plan structurally resembles an approved lesson from a past
failure, using role-and-relationship patterns in a FalkorDB graph.

Setup, the graph data model and the Cypher queries will be documented here as they're built.

## How this was built
The build is logged step by step in [`docs/diary/`](docs/diary/README.md).
AI-assistant use is disclosed in [`AI_USE.md`](AI_USE.md). Data sources: [`DATA.md`](DATA.md).

## Setup (local)
Requires Python 3.12 and [uv](https://docs.astral.sh/uv/) (or plain pip).
```bash
python3.12 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt   # or: .venv/bin/pip install -r requirements.txt
source .venv/bin/activate
```
### FalkorDB (Docker)
Requires Docker Desktop running.
```bash
docker compose up -d      # start (http://localhost:3000 for the Browser)
docker compose down       # stop, data kept
docker compose down -v    # stop AND DELETE ALL DATA (reset)
```
The image is pinned to `falkordb/falkordb:6.0.2` by digest; ports are bound to 127.0.0.1 only.
