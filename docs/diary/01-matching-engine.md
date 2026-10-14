# 01. The matching engine (first vertical slice)

## Goal
Given a plan and a lesson, compute in FalkorDB how many of the lesson's conditions the
plan meets (k of n), with consistent role bindings, and name the completion step.

## What we did
1. Set up the repo, disclosures, Python env and a pinned FalkorDB (T03–T05).
2. Verified 12 FalkorDB behaviours the engine depends on (T06).
3. Designed graph model v1 from the lesson conditions (T07, ADR-004).
4. Designed five condition kinds and an anchor-first evaluator (T08, ADR-005).
5. Wrote 12 matching tests first, then `schema.py`, `compiler.py`, `matcher.py` (T09).

## Modules and functions
- `schema.py`: `LABELS`, `RELATIONSHIPS`, `PROPERTIES`: the whitelist.
- `compiler.py`: `compile_condition(cond, anchor, bindings) -> (cypher, params)`: one condition → one query. Helpers `_start`, `_path`, `_ident`.
- `matcher.py`: `evaluate(graph, anchor, lesson) -> MatchResult`: k of n, status, bindings. Helpers `_run` (ordered, branching evaluation), `_status`.
- Change during the build: `evaluate` gained an anchor-exists check (see Problems).

## Decisions
### Count with named relationships only
- **Chose:** every hop is named (`r1`, `r2`) and counts use `count(r)`.
- **Why:** T06 showed unnamed relationships count 2 parallel edges as 1.
- **Rejected:** `count(*)` because it silently undercounts.

### Two candidates for a role → keep the highest k
- **Chose:** branch per candidate and keep the best k; ties go to the smallest id.
- **Why:** the risk is real if *any* connected channel is unwatched; the result is deterministic and explained.
- **Rejected:** "first candidate found", because the order isn't guaranteed and it could miss the risky one.

### Unbound dependents count as not holding
- **Chose:** a condition whose role couldn't be bound is `unbound` and doesn't count toward k.
- **Why:** NODUS should never claim a risk it couldn't check.
- **Rejected:** skipping it (changing n), because n would differ per plan and k-of-n stops being comparable.

## Problems and fixes
### pytest can't import nodus
- **Symptom:** collection error, `ModuleNotFoundError`.
- **Cause:** the project root wasn't on Python's import path.
- **Fix:** `pythonpath = ["."]` in `pyproject.toml`.
- **How to spot it next time:** "error during collection" before any test runs.

### Unknown anchor: crash, then k = 1
- **Symptom:** `IndexError`, then `assert (1, 'partial') == (0, 'partial')`.
- **Cause:** zero rows for a missing node; A1.2 is a company-level fact that ignores the anchor.
- **Fix:** zero rows → doesn't hold; `evaluate` checks the anchor exists first.
- **How to spot it next time:** a condition that doesn't mention the anchor will hold for *any* plan.

## Run check (exercise: predict first, then run)
- **Command** (Docker Desktop running, from `~/Desktop/nodus`):
  ```bash
  docker compose up -d && .venv/bin/pytest -v tests/test_matching.py
  ```
- **Test:** *write in your words what `test_completion_pending_is_foresight` checks, and why it matters.*
- **Predicted:** *before running, write: how many tests, pass or fail, and the hero's k/n.*
- **Actual:** *paste the last lines.*
- **Match:** *yes/no; if no, what it taught you.*
- (Claude's own run, Oct 15 03:15: 12 passed; 24 with the lab tests.)

## Plain-English summary
NODUS checks a plan against a lesson one condition at a time, inside the graph database,
always starting from the plan itself. It counts how many conditions hold. If all but the
lesson's final step hold, it says "you're one step away" and names that step.

## Teach-back (exercise)
Answer without looking, then check against the code and LOG step 12.
| Question | My answer (short) | Result |
|---|---|---|
| How is k of n computed, and why can't bindings drift between conditions? | | |
| Why does a condition that can't be bound count as *not* holding, rather than being skipped? | | |
| What would break if `_path` didn't name relationships? | | |
