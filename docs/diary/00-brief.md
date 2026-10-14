# 00. The brief (exercise)

**Status:** the live gate was skipped on Oct 15, 02:55, to save Claude usage. It's an
exercise instead. Write your answers in the "My answer" boxes *before* you open the
answer key. Opening the key first turns it into reading, not learning.

**Read first (10 min):** Part 0 of `~/Desktop/graph-hacks/NODUS_FINAL_PLAN.md`
(lines 159–232). Skip the rest.

---

## The idea in plain words

A doctor has seen a disease once. A new patient describes different symptoms in
different words, but the *pattern* is the same: fever, then rash, then joint pain, in
that order. A search tool is a doctor who only listens to the words. NODUS is the doctor
who sees the pattern.

```
 old failure:  [someone] ──pushes──► [change] ──to──► [all servers at once]   (no test stage)
 new plan:     [Priya]   ──ships───► [config] ──to──► [entire fleet]          (no canary)
                    different words, same roles and links  →  "echo"
```

---

## Q1. What is NODUS?
**My answer:**

<details><summary>Answer key</summary>

An "immune memory" for a company. It turns lessons from past failures (the company's
own post-mortems, plus famous public ones) into **patterns of roles and relationships**
stored in a FalkorDB graph, and it watches new plans for those patterns.
</details>

## Q2. What problem does it solve?
**My answer:**

<details><summary>Answer key</summary>

Companies repeat failures, even ones they wrote down, because lessons sit in a database
waiting to be searched, and people (and text search) retrieve by what things *sound*
like, not how they *work*. NASA's lessons database went unused; the Columbia report
called it "history as cause". A new plan described in new words never finds the old
lesson.
</details>

## Q3. How does it work, at a high level?
**My answer:**

<details><summary>Answer key</summary>

1. A lesson is written as a small set of **conditions** over roles and links (for example,
   "a change reaches all servers at once" and "no staged rollout"). A human approves
   every lesson, and each condition cites a source sentence.
2. Plans live in the company graph. Each condition becomes a graph query.
3. **Matching:** NODUS counts how many conditions a plan meets (k of n), keeping the
   same entity bound to the same role across conditions.
4. If k = n − 1, the missing condition is the **completion step**: the one step not to take.
5. It also flags **silence** (something that should exist but doesn't, like no owner),
   invites the **witness** (the person who raised the concern last time), and records the
   outcome so the memory improves.
6. The LLM only drafts wording and proposes lessons. It never decides a match.
</details>

## Q4. What are we choosing *not* to do?
**My answer:**

<details><summary>Answer key</summary>

- No "chat with your docs" / generic RAG; no matching by text similarity.
- The LLM doesn't decide matches or severity.
- No graph visualisation for show; the picture comes from match results.
- No JavaScript or web API: Python and Streamlit only.
- No private or real-person data: synthetic company plus public post-mortems.
- No claims of being "first"; no scores on people (witnesses are invited, never ranked).
- Lite path: Resurrection and (probably) the melody are cut.
</details>

## Prediction. A lesson has 5 conditions. If NODUS only reported 5-of-5 matches, what would it lose?
**My answer:**

<details><summary>Answer key</summary>

**Foresight.** A 5-of-5 match means the failure has already been fully set up. That's
hindsight. The value is the 4-of-5 match: the plan is *one step away*, and NODUS can
name that missing 5th condition as the step to avoid, before anyone takes it. You'd also
lose near-miss signals (3 of 5) that show a plan drifting toward a known failure.
</details>

---

When you've answered all five, rate yourself: which ones did you get right without the
key? Note any shaky ones in the "Self-check" line below and revisit them at the end of day 1.

**Self-check:**
