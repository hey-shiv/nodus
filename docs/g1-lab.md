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
