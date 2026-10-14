# Evaluation results (synthetic)

Protocol: `eval/DECLARATION.md`, committed at 03:49:55 IST on Oct 15, 2026, **before** any
evaluation data was generated. Dev (seed 101) was used only to fix the baseline threshold;
test (seed 202) was **run once** at 03:51 IST. Reproduce with:
```bash
.venv/bin/python -m eval.run dev && .venv/bin/python -m eval.run test
```

## Test split (the evidence)


B2 TF-IDF threshold t = 0.000 (chosen on dev)

| Metric | NODUS | B2 keywords (TF-IDF) |
|---|---|---|
| F1 hits | 18 of 18 | 18 of 18 |
| F2 false alarms | 0 of 18 | 18 of 18 |
| F4 false alarms | 0 of 10 | 10 of 10 |
| F3 foresight (k = n−1 and the right missing condition) | 20 of 20 | not applicable |

Descriptive (not the declared operating point): B2 at the smallest positive threshold t = 0.007 gives F1 hits 1 of 18, F2 false alarms 18 of 18, F4 false alarms 0 of 10.

**F5 adversarial cases (descriptive):**

- (a) trivial change with the full risky shape: NODUS antibody-1 5/5, full, missing none; B2 similarity 0.092 (raised)
- (b) risky shape, risk class not recorded: NODUS antibody-1 4/5, strong, missing ['A1.1']; B2 similarity 0.000 (raised)
- (c) completion replaced by a partial rollout, still off the procedure: NODUS antibody-1 4/5, foresight, missing ['A1.5']; B2 similarity 0.000 (raised)

**NODUS failures on F1/F2/F4:** none

The dev split gave identical counts (`eval/dev-output.md`).

## What this shows, and what it doesn't

- **Structure, not wording, decides.** On plans written in vocabulary that shares nothing
  with a lesson (F1), NODUS raised the right lesson 18 of 18 times. On plans written *in a
  lesson's own vocabulary* but structured safely (F2), it raised nothing (0 of 18).
- **The keyword baseline can't separate the two.** With its threshold chosen on dev by the
  declared rule, it raises everything (18 of 18 F2 false alarms). At any threshold low enough
  to stay quiet on unrelated plans, it catches almost no F1 plans (1 of 18), because those
  plans share no words with the lessons, by construction.
- **Foresight works as specified:** for plans missing exactly one (droppable) condition,
  NODUS reported k = n − 1 and named the right condition 20 of 20 times.

**Be careful with these numbers.** The families are generated from the same condition
definitions the lessons use, so a perfect score mainly shows that the graph queries
implement the lessons correctly and that word overlap is neither needed nor enough. It is
**not** evidence that NODUS works on real company data: there, roles (risk class, alert
routes, procedures) would have to be recorded or extracted, which this evaluation assumes.
Text is synthetic, n is small, and the baseline is simple (no embeddings; B1 was declared as
conditional and **was not run**, because `sentence-transformers` is a large download).

## Where NODUS loses (F5)

- **(a) A trivial change with the full risky shape** (updating the footer's copyright year,
  routine, off-procedure, one automated check, sent everywhere) gets a **full echo**. Structure
  alone can't tell that the stakes are tiny. This is the "autoimmunity" risk from the plan.
  Mitigations in the product: dismissals require a reason and feed the lesson's track record
  for human refinement; a richer model would add an impact or blast-radius role.
- **(b) Risk class not recorded:** A1.1 can't hold, so the echo drops to **strong** (4/5). Missing
  data lowers k rather than raising false confidence: by design, but it also means
  incomplete records hide risk.
- **(c) Completion replaced by a partial rollout while staying off the procedure:** **foresight**
  (4/5). Arguably correct: the plan is still one step from the shape.
