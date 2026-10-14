## Split: test (seed 202), synthetic, 69 plans

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
