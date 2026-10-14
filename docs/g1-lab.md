# G1 lab evidence

## T05: FalkorDB up, pinned, persistent (Oct 15, 2026, ~03:10 IST)

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

## T06: Tiny-graph lab (Oct 15, 2026, ~03:25 IST)

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

