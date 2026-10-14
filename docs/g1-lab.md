# G1 lab evidence

## T05: FalkorDB up, pinned, persistent (Oct 15, 2026, 03:01 IST)

| Item | Value |
|---|---|
| Image | `falkordb/falkordb:6.0.2` (newest stable on Docker Hub; `latest` had the same digest) |
| Digest | `sha256:107455e862a824e45e8e9f5a7fbfdf5e00a08b14e13eae2577c72fd9e3f59ba6` |
| Architecture | arm64 (native on Apple Silicon; the image's `ARCH=linux/amd64` env var is a build leftover, not the real platform) |
| Ports | `127.0.0.1:6379` (DB), `127.0.0.1:3000` (Browser, HTTP 200) |
| Data | named volume `nodus-data` → `/var/lib/falkordb/data` |
| Docker | 29.8.2, aarch64 |
| Python client | `falkordb` 1.8.0 |

### Persistence test: PASS
1. `CREATE (:Probe {id:'p1', at:'T05'})` in graph `persist_check`.
2. `docker compose down` (no `-v`), then `docker compose up -d`.
3. `MATCH (p:Probe) RETURN p.id, p.at` → `p1, T05`. The node survived.
4. The volume holds `dump.rdb`. Graph `persist_check` deleted afterwards.

### Findings
- **Persistence is RDB snapshots only** (`save 3600 1 300 100 60 10000`, `appendonly no`).
  A clean stop writes a snapshot; a crash or killed container loses writes since the
  last snapshot (up to 1 h if there are few writes). Fine for a demo; reload the
  synthetic world from the loader if needed. Open: turn on AOF if outcomes recorded in the demo must survive a crash.
- **Default query timeout is 1000 ms** (`FALKORDB_ARGS=... TIMEOUT 1000`). Any matching
  query slower than 1 s fails. Keep queries bounded; it's also a useful guard against runaway patterns.

## T06: Tiny-graph lab (Oct 15, 2026, 03:03 IST)

`tests/test_lab.py`: 12 tests, each on a throwaway graph `lab_<random>` (fixture in
`tests/conftest.py`). **All 12 pass** on FalkorDB 6.0.2 with client 1.8.0.

| # | Behaviour | Result on 6.0.2 | What NODUS will do |
|---|---|---|---|
| 1 | Count 2 parallel edges, relationship **named** `[r:R]`, `count(r)` | 2 ✅ | Always name relationships when counting (k of n) |
| 1 | Same, relationship **unnamed** `[:R]`, `count(*)` | **1** ⚠️ (limitation confirmed) | Never count over unnamed relationships |
| 2 | Absence: `WHERE NOT (p)-[:X]->(:Y)` | works ✅ (plan: *Anti Semi Apply*) | This is how silence conditions are written |
| 3 | Type alternation `[:A\|B]` | works ✅ | Allowed, e.g. "ships or pushes" |
| 4 | `count(DISTINCT …)`, `collect(DISTINCT …)` | works ✅ | Allowed |
| 5a | UTC epoch integers compared with `>` | works ✅ | **Chosen for time (ADR-003)** |
| 5b | Native `date()` comparison | works ✅ | Not used: docs conflict on temporal arithmetic; integers are simpler |
| 6 | `REMOVE n.p` | removes the key ✅ | Either works; prefer `REMOVE` (says what it means) |
| 6 | `SET n.p = null` | also removes the key ✅ | — |
| 7 | `ro_query` with `CREATE` | raises `ResponseError`, nothing written ✅ | Every read path uses `ro_query` |
| 8 | Undirected pattern `-[:R]-` | each pair returned **twice** ✅ (as documented) | Directed patterns only |
| 9 | Same variable in two comma-separated patterns | binds the **same node** ✅ | Basis of consistent role bindings in matching |

### EXPLAIN outputs
EXPLAIN builds the query plan without running it. Read plans bottom-up: the lowest line runs first.

**Why the unnamed count is wrong, seen in the plan:** in 1a the traverse step is
`(_anon_0)-[r:R]->(_anon_1:N)`, which walks each edge. In 1b it's
`(_anon_0)->(_anon_2:N)`, which only asks "are these nodes connected?", so two parallel edges collapse into one row.

All plans start with *Node By Label Scan* (no index yet). That's fine on toy and demo
sizes; indexes on `id` come with the loader (T12).

#### 1a count, named
`MATCH (:N {id:1})-[r:R]->(:N {id:2}) RETURN count(r)`
```
Aggregate
    Filter
        Conditional Traverse | (_anon_0)-[r:R]->(_anon_1:N)
            Filter
                Node By Label Scan | (_anon_0:N)
```

#### 1b count, unnamed
`MATCH (:N {id:1})-[:R]->(:N {id:2}) RETURN count(*)`
```
Aggregate
    Filter
        Conditional Traverse | (_anon_0)->(_anon_2:N)
            Filter
                Node By Label Scan | (_anon_0:N)
```

#### 2 absence
`MATCH (p:Plan) WHERE NOT (p)-[:OWNED_BY]->(:Person) RETURN p.id`
```
Project
    Anti Semi Apply
        Node By Label Scan | (p:Plan)
        Conditional Traverse | (p)->(_anon_1:Person)
            Argument
```

#### 3 alternation
`MATCH (:N {id:'a'})-[:SHIPS|PUSHES]->(t) RETURN t.id`
```
Project
    Conditional Traverse | (_anon_0)->(t)
        Filter
            Node By Label Scan | (_anon_0:N)
```

#### 4 distinct agg
`MATCH (:N {id:'a'})-[:R]->(t:T) RETURN count(DISTINCT t.name)`
```
Aggregate
    Conditional Traverse | (_anon_0)->(t:T)
        Filter
            Node By Label Scan | (_anon_0:N)
```

#### 5 epoch filter
`MATCH (e:E) WHERE e.at > $cut RETURN e.id`
```
Project
    Filter
        Node By Label Scan | (e:E)
```

#### 9 variable reuse
`MATCH (p:P)-[:OWNS]->(:C), (p)-[:APPROVES]->(:C) RETURN DISTINCT p.id`
```
Distinct
    Project
        Conditional Traverse | (p)->(_anon_3:C)
            Conditional Traverse | (p)->(_anon_1:C)
                Node By Label Scan | (p:P)
```


## T09: Matching prototype (Oct 15, 2026, 03:15 IST)

Modules: `nodus/schema.py` (whitelist), `nodus/compiler.py` (one template per kind),
`nodus/matcher.py` (anchor-first evaluator). Tests: `tests/test_matching.py`, **12 tests,
all green** (24 total with the lab).

| Test | Proves |
|---|---|
| all met → 5/5 `full` | k counts every holding condition |
| hero → 4/5 `foresight`, missing `[A1.5]` | the completion step is named |
| A1.3 missing instead → 4/5 `strong` | foresight only when the *completion* is what's missing |
| binding trap | an unwatched channel on *another* plan's system is never borrowed |
| two candidate channels → binds `ch-mail`, 3/4 | the branch with the highest k is kept |
| absence holds / fails when an active watcher is added | silence detection both ways |
| no alert channel → A2.2, A2.3 `unbound`, k = 0 | dependents are never true by default |
| parallel `GATED_BY` edges → A1.4 fails | named-relationship counting (T06) |
| unknown relationship → `CompileError` | whitelist works |
| injection-shaped anchor id → not in query text | values are parameters |
| unknown anchor → k = 0 | company-level conditions don't fire for a missing plan |

**Finding during T09:** A1.2 ("other plans follow a staged procedure") is a fact about the
company, so it held even for a plan id that doesn't exist (k = 1). `evaluate` now checks the anchor exists first.

### Compiled queries and EXPLAIN plans
#### A1.1: attribute_equals
```
MATCH (s:Plan) WHERE s.id = $start RETURN coalesce(s.risk_class = $value, false) AS holds, [s.id] AS ids
params: {'start': 'hero', 'value': 'routine'}

Project
    Filter
        Node By Label Scan | (s:Plan)
```

#### A1.2: present (other:Plan, binds proc)
```
MATCH (s:Plan) MATCH (s)-[r1:FOLLOWS]->(t:Procedure) WHERE s.id <> $anchor AND t.kind = $tp0 WITH DISTINCT t.id AS tid ORDER BY tid RETURN count(tid) > 0 AS holds, collect(tid) AS ids
params: {'anchor': 'hero', 'tp0': 'staged_rollout'}

Aggregate
    Sort
        Distinct
            Project
                Filter
                    Conditional Traverse | (t)<-[r1:FOLLOWS]-(s:Plan)
                        Filter
                            Node By Label Scan | (t:Procedure)
```

#### A1.3: absent (target = bound role)
```
MATCH (s:Plan) WHERE s.id = $start OPTIONAL MATCH (s)-[r1:FOLLOWS]->(t) WHERE t.id = $target RETURN count(r1) = 0 AS holds, [s.id] AS ids
params: {'start': 'hero', 'target': 'proc-staged'}

Aggregate
    Apply
        Filter
            Node By Label Scan | (s:Plan)
        Optional
            Filter
                Conditional Traverse | (t)<-[r1:FOLLOWS]-(s:Plan)
                    Argument
```

#### A1.4: count_equals
```
MATCH (s:Plan) WHERE s.id = $start OPTIONAL MATCH (s)-[r1:GATED_BY]->(t:Check) WITH count(r1) AS c, sum(CASE WHEN r1 IS NULL OR (coalesce(t.kind = $at0, false)) THEN 0 ELSE 1 END) AS bad, collect(DISTINCT t.id) AS ids RETURN c = $n AND bad = 0 AS holds, ids
params: {'start': 'hero', 'n': 1, 'at0': 'automated'}

Project
    Aggregate
        Optional Conditional Traverse | (t)<-[r1:GATED_BY]-(s:Plan)
            Filter
                Node By Label Scan | (s:Plan)
```

#### A2.1: present (2 hops, binds ch)
```
MATCH (s:Plan) MATCH (s)-[r1:TARGETS]->(n1)-[r2:ALERTS_TO]->(t:Channel) WHERE s.id = $start WITH DISTINCT t.id AS tid ORDER BY tid RETURN count(tid) > 0 AS holds, collect(tid) AS ids
params: {'start': 'hero'}

Aggregate
    Sort
        Distinct
            Project
                Conditional Traverse | (n1)-[r2:ALERTS_TO]->(t:Channel)
                    Conditional Traverse | (s)-[r1:TARGETS]->(n1)
                        Filter
                            Node By Label Scan | (s:Plan)
```

#### A2.3: absent (incoming, filtered)
```
MATCH (s) WHERE s.id = $start OPTIONAL MATCH (s)<-[r1:WATCHES]-(t:Person) WHERE t.active = $tp0 RETURN count(r1) = 0 AS holds, [s.id] AS ids
params: {'start': 'ch-mail', 'tp0': True}

Aggregate
    Apply
        Filter
            All Node Scan | (s)
        Optional
            Filter
                Conditional Traverse | (t)-[r1:WATCHES]->(s)
                    Argument
```

## G1 gate check (end of day 1 engine)

| Condition | Status |
|---|---|
| Pinned FalkorDB on localhost, persistence verified | ✅ T05 |
| Per-condition matching gives the expected k of n with consistent bindings, tested by pytest | ✅ T09 (12 tests) |
| Undocumented behaviours verified or avoided | ✅ T06 (12 tests) + map-property and pattern-as-value findings |
| D25 decided | ✅ Lite (ADR-002), re-confirmed: solo, prep incomplete |
| EXPLAIN outputs saved | ✅ above |
| Codex independent review of the ★ cards | ⏳ not done yet (needs the user to run Codex) |

**G1: passed**, except the Codex review, which is pending.
