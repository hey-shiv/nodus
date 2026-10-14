# NODUS: structural lesson matching on FalkorDB, Python-only (Streamlit)

## Invariants
- FalkorDB is the system of record. No JSON or Python fallback for matching, lessons, echoes or outcomes.
- The LLM never decides matches or severity. It only proposes lessons (human-approved) and drafts text from match results.
- Every query uses parameters. Read paths use `ro_query`. Writes are idempotent (MERGE on stable IDs).
- Name relationships when counting. Bound variable-length patterns. No `exists()` on patterns.
- No Cypher in Streamlit page files. Logic lives in modules that don't import Streamlit.
- Tests use a unique throwaway graph per test and make no real LLM calls.
- Every lesson condition cites a source sentence. Public facts come from primary sources only.

## Working style
- The builder is new to this stack and has a tight Claude usage budget: be brief, don't stop for interactive quizzes.
- Log every step in `docs/diary/LOG.md` (What / Why / First principles / Q&A / Open) and add exercises with answer keys to `docs/diary/EXERCISES.md`.
- Write tests first. Small steps. Never weaken or delete a test to make it pass.
- Ask before adding dependencies.
- Skills: `falkordb-skills` for Cypher and Docker; Superpowers TDD, systematic-debugging, verification-before-completion.
