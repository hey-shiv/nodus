# NODUS graph model v1

Written Oct 15, 2026 (plan task T07), derived from what the Lite-path lessons must
check. **Rule: no node kind or relationship without a condition (or witness rule) that needs it.**

Lite path lessons: **Antibody 1** "The trusted change, everywhere at once" (Cloudflare
2019 + CrowdStrike 2024), **Antibody 2** "The warning that went nowhere" (Knight 2012 +
GitLab 2017), and **one internal lesson** from a synthetic past episode. Exact condition
wording and source sentences come at T14/T16; this model only has to make them *checkable*.

## The three layers

```
 ┌─ WORLD (the company; synthetic) ──────────────────────────────────────────────────┐
 │                                                                                    │
 │   (Person)──OWNS──►(Plan | System | Channel | Procedure)                           │
 │   (Person)──WATCHES──►(Channel)                                                    │
 │                                                                                    │
 │   (Plan)──FOLLOWS──►(Procedure)        (Plan)──GATED_BY──►(Check)                  │
 │   (Plan)──HAS_STEP──►(Step)            (Plan)──TARGETS──►(System)──ALERTS_TO──►(Channel)
 │                                                                                    │
 │   (Person)──RAISED──►(Concern)──ABOUT──►(Plan)                                     │
 │   (Episode)──INVOLVED──►(Plan)         (Person)──AUTHORED──►(Document)             │
 │   (Episode)──DESCRIBED_IN──►(Document)                                             │
 └────────────────────────────────────────────────────────────────────────────────────┘
 ┌─ LESSONS (the immune memory's definitions) ───────────────────────────────────────┐
 │   (Lesson)──HAS_CONDITION──►(Condition)──CITES {quote}──►(Document)                │
 │   (Lesson)──LEARNED_FROM──►(Episode)        internal lessons                       │
 │   (Lesson)──LEARNED_FROM──►(Document)       public antibodies (origin: public)     │
 └────────────────────────────────────────────────────────────────────────────────────┘
 ┌─ ECHOES (the agent's memory; added at T22–T23) ───────────────────────────────────┐
 │   (Echo)──OF_LESSON──►(Lesson)   (Echo)──ON_PLAN──►(Plan)                          │
 │   (Echo)──INVITED──►(Person)     outcome, k, n, status as properties               │
 └────────────────────────────────────────────────────────────────────────────────────┘
```

## Node kinds

| Label | What it is | Key properties | Needed by |
|---|---|---|---|
| `Plan` | A piece of planned (or past) work: the **anchor** of every match | `id`, `title`, `change_type`, `risk_class`, `status` | every lesson (anchor, D08) |
| `Step` | One step of a plan | `id`, `kind`, `scope`, `at` (UTC epoch, ADR-003) | A1.5, A2.4, I4 (completion steps) |
| `Procedure` | A company procedure plans can follow | `id`, `kind` | A1.2, A1.3, I2 |
| `Check` | A gate a plan must pass | `id`, `kind` | A1.4 |
| `System` | Something a plan changes | `id`, `name` | A2.1, I3 (alerts belong to systems) |
| `Channel` | Where a system's warnings are delivered | `id`, `kind` | A2.1–A2.3, I3 |
| `Person` | A synthetic employee | `id`, `name`, `active` | A2.3, I3 (watchers); witnesses |
| `Concern` | A recorded worry about a plan | `id`, `summary`, `resolution` | witness rule 1 |
| `Episode` | A past internal incident | `id`, `title`, `at` | internal lesson; witnesses |
| `Document` | A source: synthetic post-mortem or public post-mortem | `id`, `title`, `url`, `origin` | provenance for every condition |
| `Lesson` | An approved lesson or antibody | `id`, `name`, `status`, `version`, `completion` | the immune memory |
| `Condition` | One checkable condition of a lesson | `id`, `kind`, `order`, `is_absence`, `params` | matching (T08 decides kinds) |
| `Echo` | One match of a lesson on a plan, and what happened | `id`, `k`, `n`, `status`, `outcome` | agent memory (T22–T23) |

## Relationship → which condition needs it

| Relationship | Needed by |
|---|---|
| `(Plan)-[:HAS_STEP]->(Step)` | A1.5 rollout to all, A2.4 goes live, I4 |
| `(Plan)-[:FOLLOWS]->(Procedure)` | A1.2 others follow staged rollout, A1.3 this one doesn't (absence), I2 |
| `(Plan)-[:GATED_BY]->(Check)` | A1.4 a single automated gate (**counted: always name it**, T06) |
| `(Plan)-[:TARGETS]->(System)` | A2.1, I3 (route from plan to its alerts) |
| `(System)-[:ALERTS_TO]->(Channel)` | A2.1, A2.2, I3 |
| `(Person)-[:WATCHES]->(Channel)` | A2.3 nobody active watches (absence), I3 |
| `(Person)-[:OWNS]->(…)` | witness rule 3 (owner of the bound system) |
| `(Person)-[:RAISED]->(Concern)-[:ABOUT]->(Plan)` | witness rule 1 (raised an overruled concern) |
| `(Person)-[:AUTHORED]->(Document)` | witness rule 2 (author of the post-mortem) |
| `(Episode)-[:INVOLVED]->(Plan)` | links a past incident to the plan that caused it |
| `(Episode)-[:DESCRIBED_IN]->(Document)` | its post-mortem (provenance) |
| `(Lesson)-[:HAS_CONDITION]->(Condition)` | lesson structure |
| `(Condition)-[:CITES {quote}]->(Document)` | "every condition cites a source sentence" |
| `(Lesson)-[:LEARNED_FROM]->(Episode \| Document)` | where the lesson came from |
| `Echo` relationships | agent memory, not conditions; built at T22–T23 |

## Walkthrough: every Lite condition, expressed in the model

`$plan` is the anchor plan's id. A role bound by one condition and reused by another
(like the procedure `$proc` or the channel `$ch`) is passed in as a parameter (D08).

**Antibody 1: The trusted change, everywhere at once** (n = 5)
| # | Condition | Sketch |
|---|---|---|
| A1.1 | The change is classed routine | `(p:Plan {id:$plan}) WHERE p.risk_class = 'routine'` |
| A1.2 | A staged-rollout procedure exists that other plans follow | `(pr:Procedure {kind:'staged_rollout'})<-[f:FOLLOWS]-(o:Plan) WHERE o.id <> $plan` → binds `pr` |
| A1.3 | ∅ This plan doesn't follow it | `RETURN size([(p)-[f:FOLLOWS]->(x:Procedure {id:$proc}) \| x]) = 0` |
| A1.4 | A single automated check is the only gate | `(p)-[g:GATED_BY]->(c:Check)` → `count(g) = 1` and `c.kind = 'automated'` |
| A1.5 | **Completion:** rollout reaches all targets at once | `(p)-[:HAS_STEP]->(s:Step {kind:'rollout', scope:'all'})` |

**Antibody 2: The warning that went nowhere** (n = 4)
| # | Condition | Sketch |
|---|---|---|
| A2.1 | The changed system sends automated warnings | `(p)-[:TARGETS]->(:System)-[:ALERTS_TO]->(ch:Channel)` → binds `ch` |
| A2.2 | …to a channel that isn't treated as an alert route | `ch.kind = 'email_list'` |
| A2.3 | ∅ Nobody active watches that channel | `RETURN size([(w:Person {active:true})-[r:WATCHES]->(ch) \| w]) = 0` |
| A2.4 | **Completion:** the plan goes live | `(p)-[:HAS_STEP]->(:Step {kind:'rollout'})` |

**Internal lesson** (synthetic past episode, n = 4): its conditions reuse the same
relationships (routine change, bypassed staged procedure, alerts to an unwatched
channel, rollout to all). So the hero plan can echo **two public antibodies and one
internal lesson** at once, as in the plan's Part 0. No new kinds are needed.

**Verified (scratch run, Oct 15, 03:07):** on a tiny hero graph every sketch ran and
gave the expected answer. Antibody 1: A1.1–A1.4 true, A1.5 (completion) false → **4 of 5**.
Antibody 2: A2.1–A2.3 true, A2.4 false → **3 of 4**.

**Finding:** a pattern used as a value in `RETURN` (`RETURN NOT (p)-[:X]->()`) fails with
*"Type mismatch: expected Boolean or Null but was List"*: outside `WHERE`, a pattern means
"the list of matching paths". Absence checks use `WHERE NOT (pattern)` to filter rows, or
`size([pattern comprehension]) = 0` to return true/false.

**Result:** every Lite condition can be expressed. Every relationship is used by at
least one condition or witness rule.

## Controlled vocabularies (D10: roles come from fixed lists, not guesses)

| Property | Allowed values |
|---|---|
| `Plan.change_type` | `config_change`, `code_deploy`, `infra_change`, `data_migration` |
| `Plan.risk_class` | `routine`, `standard`, `high` |
| `Plan.status` | `planned`, `in_progress`, `done` |
| `Step.kind` | `review`, `test`, `canary`, `rollout` |
| `Step.scope` | `subset`, `all` |
| `Procedure.kind` | `staged_rollout`, `change_review`, `backup_restore_test` |
| `Check.kind` | `automated`, `human` |
| `Channel.kind` | `pager`, `chat_alerts`, `email_list` |
| `Concern.resolution` | `accepted`, `overruled`, `open` |
| `Document.origin`, every world node's `origin` | `synthetic`, `public` |

## Conventions
- Every node has a stable string `id`; writes use `MERGE` on it (idempotent).
- Every world node carries `origin` and `source` (the `Document.id` that states it).
- Time is UTC epoch seconds (ADR-003).
- Directed relationships only (undirected doubles rows, T06 #8).
- Relationships are named whenever they're counted (T06 #1).
- An absence means "absent **in the recorded graph**" (plan B7).

## Deliberately left out
Personal data, message bodies, social graphs, PageRank and centrality (decoration),
`Team` nodes (no condition needs one yet), and Echo 3–5 relationships such as
`DEPENDS_ON` (Full path only, added if Antibody 3 is built).

## Added for Antibody 3 (Oct 15, after the Lite path)

| Relationship | Needed by |
|---|---|
| `(System)-[:DEPENDS_ON]->(System)` | A3.2: a recovery/status tool depends on the system the plan changes |
| `(System)-[:FALLBACK_FOR]->(System)` | A3.3 (absence): no independent fallback is recorded for that tool |

`System.kind` joins the controlled vocabularies: `service`, `recovery_tool`.
