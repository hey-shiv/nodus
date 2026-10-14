# Exercises

One block per step in `LOG.md`. Answer in your own words first, then open the key.
Shaky answers go in the self-check line; revisit them at the end of each day.

The brief (what NODUS is) has its own file: `00-brief.md`. Do that one first.

---

## Steps 0–2: Repo, Git, .gitignore

**E1.** Why does NODUS live in a new folder, not inside `graph-hacks`?
<details><summary>Key</summary>Rule 8: main work must start after 12:01 AM IST Oct 15. A fresh repo whose first commit is after that time proves the build happened during the event and that no pre-event notes were copied in.</details>

**E2.** You delete a committed `.env` file in a later commit. Is the key safe now? Why?
<details><summary>Key</summary>No. Every commit is a full snapshot kept in `.git/`. The old commit still contains the key, and anyone who clones the public repo can check it out. You'd have to revoke the key. That's why `.gitignore` comes first.</details>

**E3.** Prediction: you add `secrets.txt` to `.gitignore` *after* you've already committed it. What does `git status` show when you edit it?
<details><summary>Key</summary>It shows as modified. `.gitignore` only affects untracked files. You'd need `git rm --cached secrets.txt` to stop tracking it (and the old commits still hold it).</details>

**Self-check:**

---

## Step 3: Live rules check

**E4.** Why diff against an archive instead of just reading the live rules?
<details><summary>Key</summary>Reading shows the rules now; only a comparison shows what changed, and a change is what could break a decision already made.</details>

**E5.** In one sentence, the FalkorDB "decoration" test.
<details><summary>Key</summary>If the product still works with FalkorDB removed, the graph is decoration and doesn't qualify.</details>

**Self-check:**

---

## Step 5: Paperwork files

**E6.** Name the three disclosure files and what each one proves to a judge.
<details><summary>Key</summary>`AI_USE.md`: which AI tools were used and how output was reviewed (rules require disclosure). `DATA.md`: the data is public, synthetic or my own (rule 7). `README.md`: setup, graph model and Cypher queries (submission requirement).</details>

**E7.** Why write ADRs during the build instead of at the end?
<details><summary>Key</summary>The "why" and the rejected alternatives are freshest at the moment of the decision; by day 3 you remember what you built but not why. Judges ask why.</details>

**Self-check:**

---

## Step 6: Python environment

**E8.** What is physically inside `.venv/`, and what does "activating" it change?
<details><summary>Key</summary>A link to a Python interpreter, its own `site-packages/` with the installed libraries, and scripts in `bin/`. Activating puts `.venv/bin` first on PATH, so `python` and `pip` mean this project's copies.</details>

**E9.** Prediction: you forget to activate the venv and run `pip install groq`. Where does it go, and what breaks?
<details><summary>Key</summary>Into whatever Python is first on PATH (system or Homebrew), not the project. `import groq` then fails inside the project's venv, and `requirements.txt` never records it.</details>

**E10.** Why does `requirements.txt` list far more than the 5 packages installed?
<details><summary>Key</summary>Dependencies of dependencies. `freeze` pins them all, because any of them changing can break the app.</details>

**Self-check:**

---

## Step 8: FalkorDB in Docker

**E11.** Image, container, volume: one sentence each, with an analogy.
<details><summary>Key</summary>Image = read-only template (a class). Container = a running instance with a throwaway writable layer (an object). Volume = storage kept outside the container and mounted in (an external hard drive you plug into each new object).</details>

**E12.** Prediction: you run `docker compose down -v`, then `up -d`. Is the Probe node there? Why?
<details><summary>Key</summary>No. `-v` deletes the named volume, which held `dump.rdb`. The new container starts with an empty data folder.</details>

**E13.** What changes if the port line is `"6379:6379"` instead of `"127.0.0.1:6379:6379"`?
<details><summary>Key</summary>Docker listens on all network interfaces, so other devices on the same network can reach the passwordless database. With 127.0.0.1, only this Mac can.</details>

**E14.** Why pin by digest and not just by tag?
<details><summary>Key</summary>A tag is a movable label the publisher can re-point; a digest is a hash of the exact image bytes, so it always means the same image.</details>

**E15.** Prediction: Docker Desktop crashes 10 minutes after you recorded three outcomes. After restart, are they there?
<details><summary>Key</summary>Maybe not. Only RDB snapshots are on (save after 60 s if 10000 changes, 300 s if 100, 3600 s if 1). Three writes 10 min ago may not be snapshotted yet; a clean `down` would have saved them. AOF would fix this.</details>

**Self-check:**

---

## Step 9: Tiny-graph lab

**E16.** Prediction: `(a)-[:R]->(b)` exists three times between the same a and b. What do `count(*)` (unnamed) and `count(r)` (named `[r:R]`) return on 6.0.2?
<details><summary>Key</summary>Unnamed: 1 (only connectivity is checked). Named: 3 (each edge is walked).</details>

**E17.** Why would that bug be especially dangerous for NODUS?
<details><summary>Key</summary>Matching counts how many conditions hold (k of n). A wrong count gives a wrong k, so a wrong "completion step" or a missed echo, with no error message.</details>

**E18.** Write the Cypher for "plans with no owner". What's the plan operator called, and what does it do?
<details><summary>Key</summary>`MATCH (p:Plan) WHERE NOT (p)-[:OWNED_BY]->(:Person) RETURN p`. Anti Semi Apply: keep the row only if the inner pattern finds zero matches.</details>

**E19.** What does a pytest fixture with `yield` do before and after the test?
<details><summary>Key</summary>Before `yield`: setup (create the random-named graph), handed to the test. After `yield`: teardown (delete the graph), run even if the test fails.</details>

**E20.** Why give each test graph a random name instead of using one graph called `lab`?
<details><summary>Key</summary>No leftover data from another test (or an earlier run) can change the result, and tests can't interfere with each other or with real NODUS data.</details>

**E21.** Native `date()` comparison worked. Why still store epoch integers?
<details><summary>Key</summary>The docs conflict on temporal arithmetic and `datetime()` is undocumented; integers compare and subtract correctly with no surprises. Convert only for display.</details>

**Self-check:**

---

## Step 10: Graph model

**E22.** Property or relationship? (a) a plan is "routine", (b) a system's alerts go to a channel, (c) a step happens at a time. Why?
<details><summary>Key</summary>(a) property: a plain attribute you filter on. (b) relationship: you need to follow it and ask "who watches that channel?". (c) property (epoch int): compared, never traversed.</details>

**E23.** What's the rule for adding a node kind, and which failure does it prevent?
<details><summary>Key</summary>No node kind without a condition (or witness rule) that needs it. It prevents "graph decoration": a big graph where most nodes do no work.</details>

**E24.** Why are lessons stored in FalkorDB rather than a JSON file?
<details><summary>Key</summary>FalkorDB is the system of record (invariant). In the graph, each condition links to its cited document and each echo links to its lesson, so every answer traces back through the graph.</details>

**E25.** Condition A2.1 finds the alert channel. How does A2.3 make sure it checks the *same* channel?
<details><summary>Key</summary>A2.1 returns the channel's id; A2.3 receives it as a parameter `$ch` (anchor-first, D08). Shared bindings by construction.</details>

**E26.** Prediction: someone adds a rollout step with `scope:'all'` to the hero plan. What are k/n for Antibody 1 and Antibody 2 now?
<details><summary>Key</summary>Antibody 1: 5 of 5 (full match: the failure shape is complete). Antibody 2: 4 of 4. Both completion steps now hold, so this has turned from foresight into an active risk.</details>

**E27.** Why does `RETURN NOT (p)-[:FOLLOWS]->()` fail, and what are two correct ways to write it?
<details><summary>Key</summary>Outside WHERE a pattern is a list of paths, not a boolean. Use `WHERE NOT (p)-[:FOLLOWS]->()` to filter, or `RETURN size([(p)-[f:FOLLOWS]->(x) | x]) = 0`.</details>

**E28.** In A2.3 the watcher is an inactive person (left the company). Does the condition hold? Why does that matter?
<details><summary>Key</summary>Yes: it counts only `active:true` watchers. A channel "watched" only by someone who left is effectively unwatched. That's the GitLab/Knight shape.</details>

**Self-check:**

---

## Step 11: Condition kinds and the compiler

**E29.** "How does a lesson become queries without the AI writing any query?" Answer in 3 sentences.
<details><summary>Key</summary>Each approved condition is data: a kind plus a spec (start, path, target, bind). The compiler picks the hand-written template for that kind, checks every label/relationship/property against a whitelist, and passes all values as parameters. The same lesson always produces the same queries.</details>

**E30.** Which kind fits each? (a) "the plan has no rollback step", (b) "the plan touches exactly two systems", (c) "the plan's owner is inactive", (d) "testing happens after go-live".
<details><summary>Key</summary>(a) absent (anchor → HAS_STEP → Step {kind:rollback}). (b) count_equals (TARGETS, n=2). (c) present to bind the owner (OWNS in), then attribute_equals on `role:owner`, active = false. (d) time_order.</details>

**E31.** Why can't `FOLLOWS` be passed as `$rel`, and what protects against a malicious lesson?
<details><summary>Key</summary>Relationship types shape the query plan, so Cypher doesn't allow them as parameters. The compiler only accepts names from the graph-model whitelist and rejects anything else.</details>

**E32.** Prediction: the hero plan has NO alert channel recorded. What happens to A2.1, A2.2, A2.3, and k?
<details><summary>Key</summary>A2.1 doesn't hold (nothing to bind). A2.2 and A2.3 are "unbound" and count as not holding, explained as "couldn't check: no channel recorded". k for Antibody 2 drops to at most 1 (only A2.4 could hold).</details>

**E33.** The plan has two alert channels: one pager watched by on-call, one unwatched email list. Which does the evaluator bind as `ch`, and why?
<details><summary>Key</summary>It evaluates the dependents for both and keeps the candidate giving the highest k: the unwatched email list (A2.2 and A2.3 both hold). Ties go to the smallest id. The explanation names the chosen channel.</details>

**E34.** Status words: k=5/5? k=4/5 with the completion missing? k=4/5 with A1.1 missing?
<details><summary>Key</summary>Full; foresight; strong.</details>

**Self-check:**

---

## Step 12: Matching prototype

**E35.** What's each module's one job? (`schema`, `compiler`, `matcher`)
<details><summary>Key</summary>schema: the whitelist of names. compiler: one condition → one parameterized query. matcher: run a lesson's conditions for one anchor, in order, and count k of n.</details>

**E36.** Why write the test before the code, and why must you see it fail first?
<details><summary>Key</summary>The test fixes the definition of success before code can bend it. Seeing it fail proves the test can detect the missing behaviour; a test that never fails proves nothing.</details>

**E37.** Prediction: you delete `(:Person {id:'ex-employee'})` from the hero world. Antibody 2's k?
<details><summary>Key</summary>Still 3 of 4: A2.3 counts only active watchers, and the ex-employee was inactive. Removing them changes nothing.</details>

**E38.** Prediction: the hero's only gate becomes `kind:'human'`. Antibody 1's k and status?
<details><summary>Key</summary>A1.4 fails (not all gates automated) and A1.5 is still missing: k = 3 of 5, partial.</details>

**E39.** Read `compile_condition` for A1.1 with anchor `hero`. Write the exact query text and params.
<details><summary>Key</summary>`MATCH (s:Plan) WHERE s.id = $start RETURN coalesce(s.risk_class = $value, false) AS holds, [s.id] AS ids` with params `{'start': 'hero', 'value': 'routine'}`.</details>

**E40.** Why `coalesce(s.prop = $value, false)`?
<details><summary>Key</summary>If the property is missing, `s.prop = $value` is null, not false. coalesce turns null into false, so "no data" never counts as holding.</details>

**E41.** Why did an unknown plan id first score k = 1?
<details><summary>Key</summary>A1.2 checks *other* plans following a staged procedure, a company-level fact that doesn't depend on the anchor. Fix: verify the anchor exists before evaluating.</details>

**Self-check:**

---

## Steps 14–15: World and loader

**E42.** For each designed plan, name its demo role and what NODUS should say about it.
<details><summary>Key</summary>Hero: foresight on Antibody 1 (4/5), Antibody 2 (3/4), internal lesson (4/5). Maps: internal lesson full. Sensor (control): no echo despite CrowdStrike-like words. Scanner (near-miss): 3/5, not raised. Billing (clean): nothing.</details>

**E43.** Why must the hero share *no* keywords with the public post-mortems, and the control share *many*?
<details><summary>Key</summary>It's the experiment: a text search would flag the control and miss the hero. If NODUS catches the hero and ignores the control, it's matching structure, not words.</details>

**E44.** Prediction: you change the seed from 7 to 8. Does the hero's k change?
<details><summary>Key</summary>No. The seed only drives background plans, which all follow the staged procedure. A1.2 still holds (other plans follow it), and the hero's own structure is fixed.</details>

**E45.** Prediction: the loader used `CREATE` instead of `MERGE`, and you load twice. What's the hero's A1.4 result?
<details><summary>Key</summary>Two hero plans with the same id, two gate relationships... count_equals sees 2 GATED_BY (or duplicated rows), so "only one gate" fails. Duplicates silently corrupt counts.</details>

**E46.** Why MATCH both endpoints before MERGE-ing a relationship?
<details><summary>Key</summary>MERGE on a whole pattern creates every missing part, including new endpoint nodes. Matching first means the relationship attaches only to existing nodes.</details>

**Self-check:**

---

## Steps 16–19: Post-mortems, sources, lessons, G3

**E47.** Why must every condition cite a sentence found *verbatim*, and why wasn't the web tool's output trusted?
<details><summary>Key</summary>The antibodies name real companies; a misquote destroys credibility. The tool summarises pages with a small model, so its "quotes" can be paraphrased. Only a character-level check against the raw page proves a quote.</details>

**E48.** What three checks must a lesson pass before it can be stored? What's the fourth step before it's used?
<details><summary>Key</summary>Shape (pydantic), compiles (whitelisted names, roles bound before use), quotes verbatim. Then a human approval; only approved lessons are matched.</details>

**E49.** List three things the LLM is NOT allowed to do in NODUS.
<details><summary>Key</summary>Write the queries that run; decide a match or severity; approve or activate a lesson. (Also: invent evidence, which is caught by the verbatim check.)</details>

**E50.** Prediction: you edit the summary of an approved lesson and store it again. What happens to its version, its status and the matches?
<details><summary>Key</summary>Version goes up by 1, status goes back to "proposed", and the lesson stops matching until it's approved again (active_lessons returns only approved ones).</details>

**E51.** Why does the control plan raise nothing even though it shares 5+ key terms with the CrowdStrike text?
<details><summary>Key</summary>NODUS checks relationships, not words: the control follows the canary procedure (A1.3 fails), has a human gate (A1.4 fails) and pages a watched on-call (A2.2, A2.3 fail).</details>

**E52.** What's the honest limit of the CrowdStrike citation on A1.3?
<details><summary>Key</summary>The review doesn't say outright "no staged rollout"; it lists a staggered/canary deployment as a fix, which implies there wasn't one. The citation is marked as an inference from a remediation step.</details>

**E53.** Prediction: Gemini's quota runs out mid-proposal. What does `LLM.complete_json` do?
<details><summary>Key</summary>Gemini raises LLMError, so the next provider (local Gemma via Ollama) is tried. If that answers, its reply is cached and returned; if not, an LLMError lists both failures.</details>

**Self-check:**
