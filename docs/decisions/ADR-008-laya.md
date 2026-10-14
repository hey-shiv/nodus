# ADR-008: Laya as optional, human-confirmed role suggestions

- **Decision:** add [Laya](https://github.com/NandhaKishorM/laya) (Apache-2.0, a local text
  classifier) as an **optional** helper in `nodus/suggest.py`, for two jobs:
  1. **suggest** a plan's controlled-vocabulary roles (risk class, change type) from its text;
  2. **guess** a category for a dismissal reason (experimental).
- **Context:** NODUS's biggest stated limitation is that roles are given, not extracted.
  The user asked to use Laya somewhere in the process.
- **The guard rail:** suggestions are stored beside the real roles (`Plan.suggested_*`). The
  matcher never reads them. Only `confirm_role()`, a person's click, copies a value into the
  real role, and the agent re-runs. Without this, words would leak back into a structure-only
  decision: the control plan *sounds* risky.
- **Measured on Oct 15, 2026 (Laya 0.4.7, English checkpoint, CPU/MPS):**
  - risk class agreed with the recorded role on 4 of 5 demo plans; change type 3 of 5;
  - confidence was low (0.10–0.33), and Laya warned the checkpoint's confidence is partly uncalibrated;
  - dismissal-reason categories: 2 of 6 labelled examples right (near chance); the yes/no
    question type returned exactly 0.5 for every question, so it wasn't used.
- **So:** role suggestions are shown with their confidence and always need confirmation;
  reason categories are labelled experimental and never drive anything.
- **Alternatives:** the LLM for role suggestions (slower, heavier, same guard rail needed);
  no extraction at all (the status quo, still the default).
- **Trade-off:** PyTorch plus a ~1.7 GB checkpoint, so it lives in `requirements-laya.txt`,
  not the core install. The demo works without it.
- **Date:** 2026-10-15.
