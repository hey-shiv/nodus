# Condition kinds and the lesson compiler (design)

Plan task T08 (decisions D07 and D08). Written Oct 15, 2026. Implemented and tested in T09.

**The one-sentence idea:** a lesson is *data* (a list of conditions, each with a
*kind* and a few parameters). A small fixed set of query templates, written and
understood by me, turns that data into FalkorDB queries. **No AI writes a query that runs.**

```
 approved Lesson (data in the graph)            compiler (Python, deterministic)          FalkorDB
 ┌──────────────────────────────────┐    ┌───────────────────────────────────────┐    ┌──────────┐
 │ C1 kind=attribute_equals  spec…  │──► │ pick the template for the kind        │──► │ ro_query │
 │ C2 kind=present           spec…  │    │ check identifiers against whitelist   │    │ (params) │
 │ C3 kind=absent            spec…  │    │ values → $parameters, never in text   │    └────┬─────┘
 └──────────────────────────────────┘    └───────────────────────────────────────┘         │
                         holds? + bound role ids + evidence ids  ◄───────────────────────────┘
```

## A condition's spec

Every condition, whatever its kind, is described by the same small vocabulary:

| Field | Meaning | Example |
|---|---|---|
| `start` | where the check starts: `anchor`, a role bound earlier (`role:proc`), or `other:<Label>` (any node of that label *except* the anchor) | `anchor` |
| `path` | 1–2 hops, each `{rel, dir}` with `dir` = `out` or `in` | `[{rel:"TARGETS",dir:"out"},{rel:"ALERTS_TO",dir:"out"}]` |
| `target` | label + property filters on the far end, or a bound role | `{label:"Channel"}` / `{role:"ch"}` |
| `bind` | (optional) name to give the far-end node, so later conditions can use it | `"ch"` |
| kind-specific | `property` + `value`, `n`, `before`/`after` | |

Identifiers (labels, relationship types, property names) **can't be Cypher
parameters**, so the compiler only accepts names from the graph model's whitelist
(`docs/graph-model.md`) and rejects anything else. Every *value* is a `$parameter`.

## The kinds

Every kind returns the same shape: `holds` (true/false), `bound` (`{role: id}` for any
`bind`), `evidence` (the node ids that made it true or false, for the explanation and the SVG).

| Kind | Holds when | Inputs | Template shape (sketch) |
|---|---|---|---|
| **present** | at least one path from `start` to a matching `target` exists | start, path, target, bind? | `MATCH (s)-[r1:REL]->(t:Label) WHERE s.id = $start AND t.x = $v RETURN t.id ORDER BY t.id` |
| **absent** (silence ∅) | **no** such path exists (absent *in the recorded graph*) | start, path, target | `MATCH (s {id:$start}) RETURN size([(s)-[r:REL]->(t:Label) WHERE … \| t]) = 0` |
| **attribute_equals** | a property of the start node equals a value | start, property, value | `MATCH (s {id:$start}) RETURN s.prop = $value` |
| **count_equals** | exactly `n` paths exist, and (optionally) all their targets pass a filter | start, path, n, all_targets? | `MATCH (s {id:$start})-[r:REL]->(t:Label) RETURN count(r) = $n AND all(...)` (relationship **named**: T06 finding) |
| **time_order** | step A happens before step B (epoch ints, ADR-003) | two step filters, `before` | `MATCH (s {id:$start})-[h1:HAS_STEP]->(a:Step), (s)-[h2:HAS_STEP]->(b:Step) WHERE … RETURN a.at < b.at` |

### Changes from the plan's D07 list (and why)
- **"scope = all" is not its own kind.** It's `present` with a target filter
  (`Step {kind:'rollout', scope:'all'}`). One fewer template to write, test and explain.
- **`count_equals` is added**, because Antibody 1's "a single automated check is the only
  gate" is a *count* fact. `present` can't say "exactly one".
- **`time_order` is designed but not built yet.** No Lite condition needs it (rule: build
  only what a condition needs). It gets built if the internal lesson (T14) uses it.

## Every Lite condition mapped onto a kind (no exceptions)

| # | Condition | Kind | Spec |
|---|---|---|---|
| A1.1 | change classed routine | attribute_equals | start `anchor`, `risk_class` = `routine` |
| A1.2 | staged-rollout procedure that other plans follow | present | start `other:Plan`, path `FOLLOWS out`, target `Procedure {kind:staged_rollout}`, bind `proc` |
| A1.3 | ∅ this plan doesn't follow it | absent | start `anchor`, path `FOLLOWS out`, target `role:proc` |
| A1.4 | a single automated check is the only gate | count_equals | start `anchor`, path `GATED_BY out`, target `Check`, n = 1, all targets `kind = automated` |
| A1.5 | **completion:** rollout to all at once | present | start `anchor`, path `HAS_STEP out`, target `Step {kind:rollout, scope:all}` |
| A2.1 | changed system sends warnings | present | start `anchor`, path `TARGETS out, ALERTS_TO out`, target `Channel`, bind `ch` |
| A2.2 | …to a non-alert channel | attribute_equals | start `role:ch`, `kind` = `email_list` |
| A2.3 | ∅ nobody active watches it | absent | start `role:ch`, path `WATCHES in`, target `Person {active:true}` |
| A2.4 | **completion:** plan goes live | present | start `anchor`, path `HAS_STEP out`, target `Step {kind:rollout}` |

## The evaluator (anchor-first, D08)

For one anchor plan and one lesson:
1. Run the conditions **in order**. A condition that binds a role (A1.2 → `proc`,
   A2.1 → `ch`) comes before the conditions that use it.
2. Each condition gets the anchor id plus any bound role ids as parameters.
3. `k` = number of conditions that hold, `n` = number of conditions.
4. Status:
   - `k = n`: **full**, the shape is complete;
   - `k = n − 1` and the missing one is the lesson's completion condition: **foresight**;
   - `k = n − 1`, a different one missing: **strong**;
   - lower `k`: **partial** (below the lesson's threshold, nothing is raised).

### Edge cases, decided now
| Case | Rule |
|---|---|
| **A binder finds nothing** (no alert channel) | The dependent conditions are `unbound`: they count as **not holding** and the explanation says "couldn't check: no channel recorded". Never true by default. |
| **A binder finds two candidates** (two channels) | Evaluate the dependent conditions once per candidate and keep the candidate giving the **highest k**; ties go to the smallest id (deterministic). The explanation names the chosen one. |
| **Binding trap:** two similar entities, only one connected to the anchor | Can't fool it: candidates come only from paths that *start at the anchor* (or at a role bound from it). T09 tests this. |
| **Parallel relationships** | Every counted relationship is named (`count(r)`); T06 showed unnamed counts are wrong. |
| **Missing data vs real absence** | `absent` means "absent in the recorded graph", worded that way in the UI (plan B7). |
| **`other:<Label>` start** (A1.2) | Always excludes the anchor (`WHERE o.id <> $anchor`), so a plan can't vouch for a procedure on its own. |
| **Unknown label, relationship or property in a spec** | The compiler refuses the lesson at approval time; it never runs a half-understood query. |

## Where lessons live
`(Lesson)-[:HAS_CONDITION]->(Condition)`. A Condition node stores `kind`, `order`,
`is_absence` and `spec` (a JSON string: FalkorDB 6.0.2 rejects map properties with "Property values can only be of primitive types or arrays of primitive types", checked Oct 15).
The compiler reads them back with `ro_query`.
