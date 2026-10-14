# ADR-004: Graph model v1 (plan T07)

- **Decision:** a three-layer model (World / Lessons / Echoes) with 13 node kinds and
  relationships each justified by a Lite-path condition or witness rule. Full model and
  diagram: `docs/graph-model.md`.
- **Context:** the product only works if every lesson condition is a checkable graph
  fact. "Relationships first": start from the conditions, not from what a company has.
- **Alternatives:** (a) a generic company graph (people, teams, docs, tickets) first:
  rejected, it grows nodes no condition uses (decoration); (b) storing lessons as JSON
  outside the graph: rejected by the invariant "FalkorDB is the system of record".
- **Reason:** every condition is expressible (walkthrough verified on a tiny graph);
  the internal lesson reuses the same relationships, so the hero can echo public and internal lessons at once.
- **Trade-off:** roles come from fixed vocabularies (D10), which a real company would
  have to tag. Listed as a README limitation.
- **Date:** 2026-10-15.
