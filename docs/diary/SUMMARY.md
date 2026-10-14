# NODUS: project summary (explain it out loud from this page)

*Exercise mode: the cross-exam below is written as questions with recommended answers. Say
your answer out loud first, then open the key. Anything you get wrong goes in "Weak spots".*

## The one-page explainer

**The problem.** Companies repeat failures they already wrote down. Lessons sit in
post-mortems waiting to be searched, and people (and search tools) look by how things *sound*.
A plan in new words never finds the old lesson.

**The idea.** Store a lesson as a **shape**: 3–6 conditions about roles and relationships
("this change doesn't follow the staged procedure other changes follow"). Shapes live in a
graph, FalkorDB, because the conditions *are* relationships. Each condition quotes the exact
sentence it comes from, and a person approves the lesson.

**How it works.**
1. A plan is saved. The agent runs every approved lesson against it.
2. A compiler turns each condition into one small, parameterized Cypher query from a
   hand-written template. No AI writes a query that runs.
3. Queries start from the plan (the anchor). A role found by one condition (the channel, the
   procedure) is passed to later ones, so it stays the same thing.
4. Count the conditions that hold, k of n. All but the last step holding → **"one step away"**,
   and NODUS names that step. That's foresight.
5. Missing things are worded "not recorded in the company graph". The person who warned last
   time is invited by role. The agent stores an echo record; the owner's answer (heeded /
   dismissed with a reason / escalated) builds the lesson's track record.

**The proof.** The hero plan (different words) is one step from two public failures and one
internal one; the control plan (CrowdStrike's own words, safe structure) raises nothing. In a
pre-declared synthetic test: 18/18 echoes found, 0/18 false alarms, 20/20 missing steps named;
keyword search couldn't separate the families. It loses on a trivial change with a risky shape.

## Architecture sketch

```
            Streamlit pages (no Cypher)                         data/ (lessons, post-mortems,
   Plans · Echo · Inbox · Lessons · How it works                      sources)
        │ save plan   │ open echo   │ acknowledge   │ approve            │
        ▼             ▼             ▼               ▼                    ▼
   ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐        ┌──────────┐
   │ agent   │──►│ matcher │──►│ compiler │   │ lessons  │◄───────│ proposals│◄── llm (Gemini → Gemma)
   │ (loop)  │   │ anchor- │   │ templates│   │ validate │        │ (drafts) │
   └──┬──┬───┘   │ first   │   │+whitelist│   │ store    │        └──────────┘
      │  │       └────┬────┘   └────┬─────┘   └────┬─────┘
      │  └─► severity (pure rule)   │              │         suggest (Laya, optional,
      │  └─► witnesses, wording     │              │          human-confirmed)
      ▼                             ▼              ▼
   ┌────────────────────── FalkorDB (system of record) ───────────────────────┐
   │ WORLD: Plan Step Procedure Check System Channel Person Concern Episode   │
   │ LESSONS: Lesson Condition Document (CITES quote)    ECHOES: Echo         │
   └──────────────────────────────────────────────────────────────────────────┘
```

## Final cross-exam (a sceptical judge)

**Q1. Couldn't Postgres plus embeddings do this?**
<details><summary>Recommended answer</summary>Embeddings compare words, which is exactly what fails: our keyword baseline flagged every same-words plan and missed different-words ones. Postgres could store the facts, but each condition is a multi-hop relationship pattern with absences and role bindings (plan → system → channel ← nobody watching). That's natural, parameterized graph matching in Cypher, and the lessons, plans, echoes and their links all live in one graph. Remove FalkorDB and nothing matches.</details>

**Q2. Isn't the AI doing the real work?**
<details><summary>Recommended answer</summary>No. The AI may only draft a lesson; the draft must pass shape, whitelist and verbatim-quote checks plus a human approval. A deterministic compiler writes every query. Severity is a published rule. Heads-ups are templates filled from match results. In fact the local model's drafts all failed the checks, which is why the demo lessons are hand-authored (disclosed).</details>

**Q3. Your evaluation is perfect. Isn't it rigged?**
<details><summary>Recommended answer</summary>It's built from the same condition definitions, so it shows the queries implement the lessons and that wording is neither needed nor enough, not real-world accuracy. That's stated in RESULTS.md. It was declared and committed before data existed, the test split was run once, and it reports where NODUS loses (a trivial change with a risky shape gets a full echo).</details>

**Q4. Where do roles like "risk class" come from in a real company?**
<details><summary>Recommended answer</summary>That's the biggest limitation: in the demo they're recorded. In production they'd come from plan templates (fields people already fill in) or extraction. We added Laya to suggest roles from text, but suggestions only count after a person confirms them, so words can't leak into the structural decision.</details>

**Q5. Why does the control plan not match?**
<details><summary>Recommended answer</summary>It follows the canary procedure (A1.3 fails), has a human review (A1.4 fails) and its alerts page a watched on-call (A2.2, A2.3 fail). NODUS never reads its words.</details>

**Q6. How do you keep "the channel" the same across conditions?**
<details><summary>Recommended answer</summary>Anchor-first evaluation: every query starts at the plan; a condition that finds a channel binds its id, and later conditions receive it as a parameter. With two candidates, each is tried and the highest k wins, with ties broken by id. A test checks a channel on another plan's system is never borrowed.</details>

**Q7. What FalkorDB surprise could have broken it?**
<details><summary>Recommended answer</summary>Counting over an unnamed relationship returns 1 for two parallel edges, so "the only gate" would be wrong. Found in the lab tests before any design depended on it; every counted relationship is named. Also: a pattern in RETURN is a list, not a boolean; maps can't be properties; reads on a never-written graph raise "empty key".</details>

**Q8. How would you take this to production?**
<details><summary>Recommended answer</summary>Feed plans from where they already live (change tickets, deploy pipelines) into the graph with roles from templates; run the agent on change events; enable AOF persistence (now snapshots only) and a FalkorDB password, never exposing 6379; index id per label (done); add an impact role so trivial changes stop full-echoing; route heads-ups to the real chat/pager with human-approved sending; keep the test suite and the declared evaluation as regression checks.</details>

**Q9. Why are witnesses never scored?**
<details><summary>Recommended answer</summary>Scoring people as "right" or "wrong" turns a learning tool into blame, and people stop raising concerns. Graph distance isn't expertise either. NODUS invites by role in the original episode (who warned, who wrote the post-mortem, who owns the system) and says "no witness available" honestly.</details>

**Q10. What did you build yourself, given an AI assistant?**
<details><summary>Recommended answer</summary>(Answer in your own words.) The concept, all decisions (ADRs), the scope, the evaluation protocol and the test intentions; the diary records every step with its reasoning, and I worked through the exercises to check I understand each part.</details>

**Q11. What happens if FalkorDB is down?**
<details><summary>Recommended answer</summary>The app shows a clear error ("start it with docker compose up -d") instead of crashing; nothing falls back to Python matching, by design. Data survives a clean restart (verified); a crash can lose writes since the last snapshot.</details>

**Q12. Why Streamlit and not React?**
<details><summary>Recommended answer</summary>Python-only was a hard constraint (I know Python; four days). Streamlit gives pages and forms with no JavaScript; the centrepiece, the alignment picture, is an SVG built by a pure Python function from the match result, so it's testable.</details>

## Weak spots

*Fill in after doing the exercises and this cross-exam.* List each question you got wrong,
with the right answer in your words. (Exercises: `EXERCISES.md` E1–E77; the brief: `00-brief.md`.)

-
