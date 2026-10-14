# ADR-001: The concept

- **Decision:** build NODUS, an immune memory that matches new plans against approved
  lessons by structure (roles and relationships in FalkorDB), not by words.
- **Context:** Track 03 (Company Brain) asks for an agent over a company graph. Lessons
  databases go unused because retrieval goes by surface wording.
- **Alternatives:** knowledge-recall Q&A (crowded; generic RAG), hollow-consensus
  detection (earlier draft). Both rejected during pre-event ideation.
- **Reason:** the graph is the product: a lesson *is* a subgraph pattern, so removing
  FalkorDB removes the core feature. Partial (k of n) matches give foresight.
- **Trade-off:** pattern quality depends on human-approved lessons; few, crisp conditions.
- **Date:** 2026-10-15, confirmed at kickoff (plan T02).
