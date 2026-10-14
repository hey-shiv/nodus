# NODUS

> **Learn from mistakes you never made.**
> Different words. Same shape.

NODUS is an immune memory for a company. It turns lessons from post-mortems (the
company's own, and famous public ones) into **patterns of roles and relationships in a
FalkorDB graph**, then checks every plan against them. When a plan takes the *shape* of a
past failure, NODUS:

- shows the old failure and the new plan side by side, condition by condition;
- names the **one remaining step** that would complete the repeat (foresight, not hindsight);
- points out what is **not recorded** in the graph (no one watching the alerts, no owner);
- invites **the person who warned last time**, by their role in the original episode;
- plays the match as an **unfinished melody**: one note per condition, the last one held back;
- **remembers** what the team did about it, so each lesson builds a track record.

Built for **Graph Hacks (FalkorDB × WeMakeDevs), Oct 15–18, 2026**.
Track: **03 Company Brain** (see [Tracks](#tracks)). Demo video: *link added at submission*.

---

## Why a graph, and why it can't be removed

People and text search retrieve lessons by what they *sound* like. NASA's lessons database
went unused for exactly this reason. The two cases below defeat any wording-based search:

| Plan (synthetic company) | Words overlap with CrowdStrike/Cloudflare? | Structure | NODUS |
|---|---|---|---|
| Refresh tariff tables for every depot | almost none | routine, skips the staged procedure others follow, one automated check, alerts to an unwatched list | **one step away** from 2 public failures and 1 internal one |
| Global rollout of dock sensor content update | lots ("global rollout", "content update", "validator", "channel file") | follows the canary procedure, human review, alerts page a watched on-call | **nothing** |

In NODUS a lesson **is** a subgraph pattern and finding an echo **is** pattern matching in
FalkorDB. Remove FalkorDB and there is nothing left to match: lessons, plans, matches, echoes
and outcomes all live in the graph. No JSON or Python fallback exists.

## Quick start (local, about 5 minutes)

Requires Docker Desktop, Python 3.12 and [uv](https://docs.astral.sh/uv/) (or pip).

```bash
git clone https://github.com/hey-shiv/nodus && cd nodus
docker compose up -d                                   # FalkorDB 6.0.2 on 127.0.0.1:6379
python3.12 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt   # or: .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/setup_demo.py --approve       # load the synthetic world + 3 lessons
.venv/bin/streamlit run app.py                         # http://localhost:8501
```

In the app, use **Reset the demo** in the sidebar at any time. Then:
1. **Plans:** the hero plan is "one step away" on three lessons, and the photo-archive plan on a fourth. Open **Compare with keyword search**.
2. **Echo:** the past failure beside the plan, every condition with its source sentence. Under **Hear it**, play the unfinished melody, then the resolved one.
3. **Plans → Change a plan:** add a *rollout* to *every target* and save. Foresight becomes a full echo.
4. **Inbox** (viewing as Lena Brandt, the owner): record what you'll do. Asha Rao, who warned last time, has an invitation.
5. **Lessons:** the track record updates; lessons can be approved, rejected, or drafted by an LLM.

Database commands: `docker compose down` stops it (data kept); `docker compose down -v`
**deletes all data**. The FalkorDB Browser is at http://localhost:3000.

**Optional LLM** (only for drafting lessons): copy `.env.example` to `.env`. Use a free
Google AI Studio key (no billing) and/or a local model: `ollama pull gemma4:12b-it-qat`.
Check with `.venv/bin/python scripts/llm_check.py`. The demo needs neither.

**Optional Laya** (role suggestions a person must confirm; experimental reason sorting):
`uv pip install --python .venv/bin/python -r requirements-laya.txt`. It appears under
*Plans → Suggest roles from the plan's text*. See [ADR-008](docs/decisions/ADR-008-laya.md).

**Tests:** `.venv/bin/pytest` (needs the database running; every test uses its own throwaway graph).

## Graph data model

```
 WORLD (synthetic company)
   (Person)-[:OWNS]->(Plan | System | Channel | Procedure)    (Person)-[:WATCHES]->(Channel)
   (Plan)-[:FOLLOWS]->(Procedure)      (Plan)-[:GATED_BY]->(Check)
   (Plan)-[:HAS_STEP]->(Step)          (Plan)-[:TARGETS]->(System)-[:ALERTS_TO]->(Channel)
   (Person)-[:RAISED]->(Concern)-[:ABOUT]->(Plan)
   (Episode)-[:INVOLVED]->(Plan)       (Episode)-[:DESCRIBED_IN]->(Document)<-[:AUTHORED]-(Person)
   (System)-[:DEPENDS_ON]->(System)    (System)-[:FALLBACK_FOR]->(System)      recovery tools and their fallbacks
 LESSONS (the immune memory's definitions)
   (Lesson)-[:HAS_CONDITION]->(Condition)-[:CITES {quote}]->(Document)
   (Lesson)-[:LEARNED_FROM]->(Episode | Document)
 ECHOES (the agent's memory)
   (Echo)-[:OF_LESSON]->(Lesson)   (Echo)-[:ON_PLAN]->(Plan)   (Echo)-[:INVITED]->(Person)
```

Every node kind and relationship exists because some lesson condition or witness rule
needs it ([docs/graph-model.md](docs/graph-model.md), ADR-004). Every node has a stable `id`
(indexed; writes are `MERGE`), `origin` (`synthetic` or `public`) and `source`. Time is UTC epoch seconds.

## How it works

1. **Lessons are data.** Each lesson has 3–6 conditions of four kinds: `present`, `absent`,
   `attribute_equals`, `count_equals` ([docs/condition-kinds.md](docs/condition-kinds.md)).
   Each condition quotes the sentence it comes from, verified word for word
   (`scripts/verify_sources.py`: 26/26 quotes; for the SEC page set `NODUS_CONTACT="Your Name you@example.com"`, which sec.gov requires of automated requests). A person approves a lesson before it is used.
2. **A deterministic compiler** (`nodus/compiler.py`) turns each condition into one
   parameterized query from a hand-written template. Labels and relationship types are
   checked against a whitelist; every value is a `$parameter`. **No AI writes a query that runs.**
3. **Anchor-first matching** (`nodus/matcher.py`) runs the conditions for one plan in order,
   with `ro_query`. A role found by one condition (the channel, the procedure) is passed to
   later ones, so "the channel" means the same channel throughout. Two candidates? The branch
   with the highest k wins, ties by id.
4. **Severity is a published rule** (`nodus/severity.py`): n of n = full; n − 1 with the
   completion step missing = **foresight**; n − 1 otherwise = strong; ≥ half = note.
5. **The agent loop** (`nodus/agent.py`) runs when a plan is saved: match → decide →
   heads-up (template-filled from the match) and witness invitation → **remember** an Echo
   record with a stable id. The owner records heeded / dismissed (a reason is required) /
   escalated; the lesson's track record is counted from outcomes. It never edits a plan or approves anything.
6. **The unfinished melody** (`nodus/melody.py`): a pure function renders the match as WAV audio.
   Each condition is a note in condition order with the completion step last; conditions that hold
   play, an absence is a short rest, and the completion step's note (the tonic that resolves the
   phrase) is held back as silence. "Resolved" plays it. It carries nothing that isn't in the match,
   never autoplays, and the alignment picture is its visual equivalent.
7. **Witnesses** (`nodus/witnesses.py`) by role, in order: an active person whose concern in the
   original episode was overruled → the post-mortem's author → the owner of the system. Public
   lessons cite their documents, never people. Graph distance is never used as "expertise".

## The Cypher NODUS depends on

These are the actual compiled queries for the hero plan (from `compile_condition`):

```cypher
// A1.2  present: a staged procedure that OTHER plans follow (binds `proc`)
MATCH (s:Plan) MATCH (s)-[r1:FOLLOWS]->(t:Procedure)
WHERE s.id <> $anchor AND t.kind = $tp0
WITH DISTINCT t.id AS tid ORDER BY tid
RETURN count(tid) > 0 AS holds, collect(tid) AS ids

// A1.3  absent (silence): this plan does not follow that procedure
MATCH (s:Plan) WHERE s.id = $start
OPTIONAL MATCH (s)-[r1:FOLLOWS]->(t) WHERE t.id = $target
RETURN count(r1) = 0 AS holds, [s.id] AS ids

// A1.4  count_equals: a single automated check is the only gate (relationship NAMED: see below)
MATCH (s:Plan) WHERE s.id = $start
OPTIONAL MATCH (s)-[r1:GATED_BY]->(t:Check)
WITH count(r1) AS c,
     sum(CASE WHEN r1 IS NULL OR (coalesce(t.kind = $at0, false)) THEN 0 ELSE 1 END) AS bad,
     collect(DISTINCT t.id) AS ids
RETURN c = $n AND bad = 0 AS holds, ids

// A2.1  present, two hops: the changed system's alert channel (binds `ch`)
MATCH (s:Plan) MATCH (s)-[r1:TARGETS]->(n1)-[r2:ALERTS_TO]->(t:Channel)
WHERE s.id = $start
WITH DISTINCT t.id AS tid ORDER BY tid
RETURN count(tid) > 0 AS holds, collect(tid) AS ids

// A2.3  absent, incoming: nobody active watches that channel
MATCH (s) WHERE s.id = $start
OPTIONAL MATCH (s)<-[r1:WATCHES]-(t:Person) WHERE t.active = $tp0
RETURN count(r1) = 0 AS holds, [s.id] AS ids
```

Witness rule 1 (`nodus/witnesses.py`): a walk from the lesson to the person who warned:
```cypher
MATCH (l:Lesson {id: $id})-[a:LEARNED_FROM]->(e:Episode)-[b:INVOLVED]->(past:Plan)
      <-[c:ABOUT]-(con:Concern)<-[d:RAISED]-(p:Person {active: true})
WHERE con.resolution IN ['overruled', 'open']
RETURN DISTINCT p.id, p.name, con.summary, e.title ORDER BY p.id
```

Agent memory (`nodus/agent.py`): one Echo per lesson × plan, updated, never duplicated:
```cypher
MATCH (l:Lesson {id: $lid}), (p:Plan {id: $pid})
MERGE (e:Echo {id: $eid})
ON CREATE SET e.created_at = $now, e.times_seen = 0
SET e.k = $k, e.n = $n, e.level = $level, ..., e.times_seen = e.times_seen + 1,
    e.status = CASE WHEN e.outcome IS NULL THEN 'open' ELSE 'acknowledged' END
MERGE (e)-[:OF_LESSON]->(l) MERGE (e)-[:ON_PLAN]->(p)
```

**FalkorDB behaviours verified before relying on them** (`tests/test_lab.py`, [docs/g1-lab.md](docs/g1-lab.md)):
counting over an **unnamed** relationship returns 1 for two parallel edges (so every counted
relationship is named); `WHERE NOT (pattern)` works (plan operator *Anti Semi Apply*); a pattern
used as a value in `RETURN` is a list, not a boolean; maps can't be property values; reads on a
never-written graph raise "empty key"; the default query timeout is 1 s.

## Evaluation (synthetic)

Declared in [eval/DECLARATION.md](eval/DECLARATION.md) and committed **before** any evaluation
data existed; test split run once. It covers the three lessons it declared; Antibody 3 was added
later and is **not** part of these numbers. Full results and limits in [eval/RESULTS.md](eval/RESULTS.md).

| Test split (synthetic) | NODUS | Keyword search (TF-IDF) |
|---|---|---|
| F1 same structure, different words: right lesson raised | 18 of 18 | 18 of 18 at t = 0 (1 of 18 at the smallest t > 0) |
| F2 same words, different structure: false alarms | 0 of 18 | 18 of 18 |
| F4 unrelated: false alarms | 0 of 10 | 10 of 10 |
| F3 one condition missing: k = n − 1 and the right one named | 20 of 20 | n/a |

**Read this carefully:** the families are generated from the same condition definitions the
lessons use, so this shows that the queries implement the lessons and that wording is neither
needed nor enough. It does **not** show accuracy on real company data. **Where NODUS loses:** a
trivial footer-year change with the risky shape gets a full echo, because structure can't see
stakes. The embedding baseline was declared but not run.

## Limitations

- **Roles are given, not extracted.** Risk class, alert routes and procedures are recorded in
  the synthetic world. A real deployment needs them from plan templates or extraction. An
  optional [Laya](https://github.com/NandhaKishorM/laya) step *suggests* risk class and change
  type from a plan's text (4 of 5 and 3 of 5 agreed with the recorded roles on the demo plans,
  at low confidence). A suggestion never affects matching until a person confirms it.
- **Absent means absent in the recorded graph.** NODUS can't see what was never recorded.
- **Small, synthetic world;** five public incidents; hand-authored lessons (an LLM drafting
  path exists and is checked).
- **Structure can't see stakes** (see the evaluation). Dismissal reasons are the feedback path.
- NODUS flags **structural resemblance to approved lessons**. It does not predict incidents.

## Public sources

Real companies appear only as cited sources, quoted verbatim with neutral wording:
[Cloudflare, Jul 2 2019](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/),
[CrowdStrike, Jul 19 2024](https://www.crowdstrike.com/falcon-content-update-remediation-and-guidance-hub/),
[U.S. SEC on Knight Capital, 2012](https://www.sec.gov/news/press-release/2013-222),
[GitLab, Jan 31 2017](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/),
[AWS S3, Feb 28 2017](https://aws.amazon.com/message/41926/).
NODUS cites and summarises; it doesn't redistribute these pages (they're cached locally, gitignored).

## Tracks

- **Track 03: Company Brain** (primary): people, plans, systems, documents and decisions in one
  graph; who owns and who knows what (witnesses); decisions traced to their source (every condition cites a sentence).
- Also fits **Track 01** (an agent that uses the graph to decide and act) and **Track 02** (memory
  that persists and updates: echoes, outcomes, track records). The final track choice is made at submission.

## How this was built (disclosures)

- **AI use:** see [AI_USE.md](AI_USE.md). Claude Code drafted code from function lists and tests
  I approved; every step, decision and problem is logged in [docs/diary/](docs/diary/README.md).
- **Data:** see [DATA.md](DATA.md). Synthetic company plus cited public post-mortems; no private data.
- **Pre-event work** was limited to learning, notes, research and diagrams, as rule 8 allows. This
  repository was created after the event started (first commit: Oct 15, 2026, 02:59 IST).
- **Decisions:** [docs/decisions/](docs/decisions/) (ADR-001 to ADR-009).

## Project layout

```
nodus/            the engine (no Streamlit imports)
  schema.py       whitelist of labels, relationships, properties
  compiler.py     condition → parameterized Cypher (one template per kind)
  matcher.py      anchor-first evaluation, k of n, bindings
  lessons.py      validation (shape, compiles, verbatim quotes), storage, approval, versions
  severity.py     the published severity rule
  witnesses.py    whom to invite, by role
  wording.py      template sentences from match results
  agent.py        on_plan_saved, echo memory, outcomes, track record
  watch.py        all lessons × all current plans (two stages)
  world.py        the seeded synthetic company
  loader.py       idempotent UNWIND + MERGE
  llm.py          Gemini → local Gemma fallback, disk cache
  proposals.py    LLM lesson drafts, checked before storage
  suggest.py      optional Laya role suggestions (human-confirmed) and reason guesses
  baseline.py     TF-IDF keyword baseline
  svg.py          the alignment picture (a pure function)
  melody.py       the unfinished melody, as WAV bytes (a pure function)
app.py, app_pages/  Streamlit UI (no Cypher in page files)
data/             lessons, synthetic post-mortems, source registry
eval/             declaration, generator, runner, results
docs/             graph model, condition kinds, lab evidence, ADRs, build diary
tests/            pytest suite (each test on its own throwaway graph)
```

MIT licensed.
