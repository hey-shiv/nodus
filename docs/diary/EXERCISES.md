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

---

## Steps 20–21: Keys, severity, witnesses, agent, memory

**E54.** Where does the Gemini key live, how does the code read it, and why never in code?
<details><summary>Key</summary>In `.env` (gitignored). python-dotenv loads it into the environment at startup; the code reads `os.environ["GEMINI_API_KEY"]`. Code is public; a committed key stays in Git history forever.</details>

**E55.** Severity for: (a) 3/3, (b) 2/3 with the completion missing, (c) 2/3 with another missing, (d) 2/4, (e) 1/4?
<details><summary>Key</summary>(a) full (b) foresight (c) strong (d) note (exactly half) (e) ignore.</details>

**E56.** Why is `level()` a pure function, and what does that buy you?
<details><summary>Key</summary>It depends only on its inputs: no database, clock or UI. Same input → same output, so one test per table row proves it, and severity is a visible rule rather than a judgement.</details>

**E57.** The internal lesson's episode has: Asha (active, overruled concern), Tomas (active, wrote the post-mortem), Lena (owns the system). Who's invited? What if Asha leaves?
<details><summary>Key</summary>Asha (rule 1). If she becomes inactive: Tomas (rule 2, author). If he leaves too: the active owner of a system the plan targets (rule 3). Otherwise nobody, shown honestly.</details>

**E58.** Prediction: you save the hero plan 5 times. How many Echo nodes exist for it, and what's `times_seen`?
<details><summary>Key</summary>3 Echo nodes (one per lesson, ids `echo:<lesson>:plan-hero`), each with times_seen = 5. MERGE on the stable id prevents duplicates.</details>

**E59.** The owner adds the hero to the canary procedure and saves. What happens to the internal-lesson echo?
<details><summary>Key</summary>Q.2 now fails → k = 3/5 → note (not a warning). The existing echo is kept and marked "cleared"; the memory isn't deleted.</details>

**E60.** Why must a dismissal have a reason?
<details><summary>Key</summary>Reasons are the learning signal: many dismissals with the same reason suggest the lesson is too broad, and a human reviews it (B10). A bare "dismiss" teaches nothing.</details>

**Self-check:**

---

## Step 22: The app

**E61.** What happens, step by step, when the owner presses **Save plan**?
<details><summary>Key</summary>Streamlit re-runs the page with the form values → the page calls nodus.plans (set_follows, set_gate, remove_step, add_step) to write the plan → nodus.agent.on_plan_saved runs every approved lesson (read-only), computes severity, writes/updates Echo records with heads-up and witness → the page stores a summary in session_state and reruns to show the new state.</details>

**E62.** Why is there no Cypher in the page files?
<details><summary>Key</summary>Pages handle display only; all graph logic lives in modules that don't import Streamlit, so it can be tested with pytest and reused. It's also one place to review every query.</details>

**E63.** Why use `st.form` for the plan editor?
<details><summary>Key</summary>Without a form every widget change reruns the script immediately. A form batches the inputs and only acts when Save is pressed: one save, one agent run.</details>

**E64.** Read the shape strip ●●●●◌ (last one a dashed red ring). What does it mean?
<details><summary>Key</summary>Four of five conditions hold (filled dots; violet would be absences); the fifth is the completion step and is missing: foresight, "one step away".</details>

**E65.** Prediction: you edit `nodus/svg.py` while the app is running and reload the browser. Do you see the change?
<details><summary>Key</summary>Not without a file watcher: Streamlit keeps the imported module in memory. Restart the server (or install watchdog).</details>

**Self-check:**

---

## Step 23: Evaluation

**E66.** Why was the declaration committed before generating any evaluation data?
<details><summary>Key</summary>So the questions, metrics and threshold rule can't be chosen after seeing results. The commit timestamp (earlier than the data) proves it.</details>

**E67.** What do F1 and F2 test, and why do they need each other?
<details><summary>Key</summary>F1: same structure, different words (does it find echoes text search misses?). F2: same words, different structure (does it stay quiet when text search panics?). A method that raises everything passes F1 and fails F2; one that raises nothing does the reverse. Together they show discrimination.</details>

**E68.** NODUS scored perfectly. Give the honest reason this isn't proof it works on real companies.
<details><summary>Key</summary>The families were generated from the same condition definitions the lessons use, and roles (risk class, alert routes) are given rather than extracted from messy real records. It proves the queries implement the lessons and that wording doesn't matter, not real-world accuracy.</details>

**E69.** Where did NODUS lose, and what's the product answer?
<details><summary>Key</summary>F5(a): a trivial footer-year change with the risky shape got a full echo; structure can't see stakes. Answer: dismissal reasons feed the track record for human refinement; a richer model could add an impact/blast-radius role.</details>

**E70.** Why did the keyword baseline's threshold come out as 0?
<details><summary>Key</summary>F1 texts share no words with the lessons (similarity 0), so the only way to catch them is t = 0, which also flags every F2 plan. The declared rule (maximise hits − false alarms) ties at that point: the baseline can't separate the families.</details>

**Self-check:**

---

## Step 25: Laya

**E71.** Why can't Laya's suggested risk class go straight into `Plan.risk_class`?
<details><summary>Key</summary>Laya reads words. If its guess set a real role, a plan that only *sounds* routine could make A1.1 hold: wording would leak back into a structure-only decision. Suggestions live in separate properties that no query reads, until a person confirms.</details>

**E72.** Prediction: Laya suggests "routine" for the dock-sensor plan (recorded "standard"), and nobody confirms. What's Antibody 1's k for that plan? And after Kai confirms?
<details><summary>Key</summary>Unchanged (2 of 5) while it's only a suggestion. After confirmation A1.1 holds, so k = 3 of 5 (a note, still not raised). Both cases are tests in tests/test_suggest.py.</details>

**E73.** Classifier vs generative model: what's the difference, and why does it matter here?
<details><summary>Key</summary>A classifier picks from given labels with a probability; a generative model writes free text. Laya can only output allowed vocabulary values, which fits roles, but its accuracy and calibration still limit it (low confidence here).</details>

**E74.** Laya sorted 2 of 6 dismissal reasons correctly. What did we do with that, and why not delete the feature?
<details><summary>Key</summary>Kept it, as requested, but labelled experimental, shown next to the original reasons, and never used for any decision. Reporting the measured accuracy is more honest than hiding or overselling it.</details>

**E75.** Why did a failed install report success, and how do you check properly?
<details><summary>Key</summary>`cmd | tail` returns tail's exit code, not cmd's. Check that the package imports (`python -c "import google.genai"`), or use `set -o pipefail`.</details>

**Self-check:**

---

## Step 26: Real AI drafts

**E76.** Gemma's drafts failed three different ways. Name them and which check caught each.
<details><summary>Key</summary>Completion not among the conditions (pydantic model validator); `all_targets: true` instead of an object (pydantic field type); a role used before it was bound (model validator's bound-role check). None reached the database or a human.</details>

**E77.** Why is "all drafts rejected" a good outcome for the product, even though it's a bad outcome for the model?
<details><summary>Key</summary>It shows the checks work: an imperfect model can't put a malformed or unsupported lesson in front of a reviewer, let alone into matching.</details>

**Self-check:**

---

## Step 28: Keys, caches, and a draft that passed

**E78.** The Gemini draft passed every automatic check. Why isn't that enough to approve it?
<details><summary>Key</summary>The checks prove shape, allowed names and verbatim quotes, not judgement. This draft dropped "sent to every depot at once" and picked a weak completion step. Only a person can decide whether it's the right lesson.</details>

**E79.** A "Gemini" call returned in 0 seconds with Gemma's old answer. What was wrong, and what's the general rule?
<details><summary>Key</summary>The cache key was only the prompt, so a reply from one model was served for another. Rule: a cache key must include everything that changes the answer (here, the provider and model).</details>

**Self-check:**

---

## Step 29: Stricter checks

**E80.** Why does an "absent" condition on `Procedure {name: "canary procedure"}` cause false alarms on every plan?
<details><summary>Key</summary>No node has that name, so the pattern never matches, and "absent" (zero matches) is always true. Filters must use controlled vocabularies that the data actually uses.</details>

**E81.** What does path type-checking catch? Give the example from today.
<details><summary>Key</summary>Hops that can't exist in the model, e.g. Plan -ALERTS_TO-> Channel. Alerts come from the System (Plan -TARGETS-> System -ALERTS_TO-> Channel), so that condition could never hold.</details>

**E82.** The final AI draft passed all checks but missed the hero. Why, and whose job was it to catch?
<details><summary>Key</summary>Its "nobody watches" condition counted any watcher, including an inactive one (Ravi left). That's a judgement error, not a type error, so it's the human reviewer's job at approval.</details>

**Self-check:**

---

## Step 30: Antibody 3 and the melody

**E83.** Write Antibody 3's four conditions in plain words. Which one is the silence, and which is the completion?
<details><summary>Key</summary>(1) the change acts on a core system; (2) a recovery/status tool depends on that system; (3) ∅ no fallback is recorded for that tool (the silence); (4) the change hits everything at once (the completion).</details>

**E84.** Why does the billing plan stay quiet on Antibody 3 even though its recovery console depends on billing?
<details><summary>Key</summary>A mirror is recorded as FALLBACK_FOR the console, so the absence A3.3 fails: 2/4, below the warning level.</details>

**E85.** Why was the evaluation pinned to three lessons before adding Antibody 3?
<details><summary>Key</summary>The declaration named three lessons and its numbers are published. Letting a new lesson into the run would change a pre-declared result after the fact. A new evaluation would need a new declaration first.</details>

**E86.** Prediction: the hero plan adds "rollout to every target". What does the Antibody 1 melody do now?
<details><summary>Key</summary>The completion condition holds, so the phrase plays to the end: four tension notes (one a ∅ rest), then the tonic. The "Resolved" player is replaced by "resolves on its own".</details>

**E87.** Why is the melody not decoration?
<details><summary>Key</summary>It's generated only from the match result (which conditions hold, which is the completion step), carries no extra information, has a visual equivalent, and never autoplays.</details>

**Self-check:**

## Deployment and latency (steps 33–34)

1. A page makes 40 database reads one after another, and each round trip takes 120 ms. Roughly how long
   does it take? If you run them 8 at a time, what's the best case?
   <details><summary>Answer</summary>40 × 120 ms = 4.8 s. Eight at a time: 5 rounds × 120 ms ≈ 0.6 s, as
   long as the reads don't depend on each other.</details>
2. Why couldn't all 130 reads in the plans page run at the same time, even in principle?
   <details><summary>Answer</summary>Within one plan-and-lesson check, later conditions use what earlier
   ones bound (for example `sys`, then `tool`), so those reads must happen in order. Only separate checks
   are independent.</details>
3. The logs said `bom1`, but moving the API to `iad1` changed nothing. What did `bom1` actually describe?
   <details><summary>Answer</summary>The edge region that received the request (close to the visitor),
   not the region where the function ran. Check `vercel inspect`, which lists each function's region.</details>
4. Why does every visitor get their own copy of the graph?
   <details><summary>Answer</summary>So one visitor's edits can't change what the next one sees. Each visit
   starts from the same known state, and old copies are cleaned up.</details>
