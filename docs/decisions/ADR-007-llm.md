# ADR-007: The LLM's place, and cost (plan D13)

- **Decision:** the product's LLM use is limited to **proposing lesson drafts** and is
  optional. A provider-neutral wrapper (`nodus/llm.py`) with a disk cache supports a
  local Ollama model or a free-tier API chosen by an environment variable, with nothing
  configured by default. All user-facing wording (heads-ups, silence lines) comes from
  **deterministic templates** filled from match results.
- **Context:** no budget for paid APIs (no card may be attached); no local model
  installed on Oct 15; the invariant says the LLM never decides matches or severity.
- **Alternatives:** require a free-tier key (adds a setup step for judges, rate limits
  during the demo); LLM-written heads-ups (wording could drift from the evidence).
- **Reason:** the engine and demo work with **zero keys and zero cost**; every sentence
  shown is traceable to graph results.
- **What this means for the lessons:** the lessons used in the demo were **hand-authored**
  (the plan's disclosed fallback) and pass the same validation an LLM proposal must:
  pydantic shape + every cited sentence found verbatim in its source.
- **Date:** 2026-10-15.
