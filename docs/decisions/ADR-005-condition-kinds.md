# ADR-005: Condition kinds and the deterministic compiler (plan D07, D08)

- **Decision:** lessons are data; each condition has one of five kinds (`present`,
  `absent`, `attribute_equals`, `count_equals`, `time_order`) with a small spec; one
  hand-written, parameterized template per kind turns it into a query. Evaluation is
  anchor-first: bound roles are passed to later conditions as parameters. Design:
  `docs/condition-kinds.md`.
- **Context:** rule 12 requires understanding the code; the invariant says the LLM never
  decides matches. Matching must be deterministic and testable.
- **Alternatives:** (b) the LLM writes Cypher per lesson: rejected (unexplainable,
  injection risk, non-deterministic); (c) hand-written queries per lesson: rejected as
  the main path (doesn't scale, lessons stop being data), kept as a disclosed emergency fallback for one hero lesson.
- **Changes vs plan D07:** "scope = all" folded into `present` (it's a target filter);
  `count_equals` added (needed by A1.4); `time_order` designed, built only if a lesson needs it.
- **Reason:** all 9 Lite antibody conditions map onto a kind with no exceptions.
- **Trade-off:** lessons can only say what the kinds can say. That's intended: it keeps lessons crisp (plan B3).
- **Date:** 2026-10-15.
