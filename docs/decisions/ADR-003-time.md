# ADR-003: How time is stored (plan D09)

- **Decision:** UTC epoch integers (seconds) for every time property. Convert to IST only for display.
- **Context:** lessons may need "before"/"after" conditions. The FalkorDB docs conflict
  on temporal arithmetic and don't document `datetime()`.
- **Alternatives:** native temporal types (comparison works on 6.0.2, tested in T06,
  but arithmetic is unclear); no time at all, step-order numbers instead.
- **Reason:** integers always compare and subtract correctly, and are tested (T06 #5a).
- **Trade-off:** less readable in the Browser; needs a display helper.
- **Date:** 2026-10-15.
