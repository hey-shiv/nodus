# Build log

Newest entries at the bottom. Times are IST.

---

## Step 0: Kickoff decisions (Thu Oct 15, 02:40)

**What:** before creating anything, settled four things: where the repo lives, where
this diary lives, who is on the team, and how much of the prep I'd done.

**Why:** each one changes what happens next. The repo location matters for the rules
(see first principles). The diary location decides who can read it. Team size decides
the scope. Prep level decides how much each step needs explaining.

**First principles: why a brand-new folder?**
Graph Hacks rule 8 says the main coding and design work must begin after the event
starts (12:01 AM IST, Oct 15). Before that, only notes, ideas and diagrams were allowed.
My planning folder `~/Desktop/graph-hacks` holds months of notes and research. If I
built inside it, nobody could tell planning from building. A fresh, empty folder with
its own Git history proves it: the first commit's timestamp is after the start, and
everything in the repo was made during the event. The planning notes are never copied
in (plan decision D26).

**Q&A:**
- **Q (Claude): Where should the event repo live?**
  A: `~/Desktop/nodus`, next to `graph-hacks`. `graph-hacks` stays a read-only archive.
- **Q (Claude): Should the diary be public, inside the repo?**
  A: Yes, `docs/diary/` in the public repo, so judges can see I understood each step.
- **Q (Claude): Is the team still just me?**
  A: Solo. So the plan's **Lite path** (D25) is the default: fewer features, same core.
- **Q (Claude): How much of the 6-day prep curriculum did I finish?**
  A: Only Day 1 (venv, Git, Docker basics, a first graph), because I was ill. That's why
  this diary explains everything from first principles.

**Open:**
- Only Day 1 of prep is done, so Days 2 to 6 (Cypher, the Python client, Streamlit, the
  LLM, evaluation) get learned during the build. That costs time, so the Lite path and
  the plan's cut order (D-5) matter even more.

---

## Step 1: Create the repo folder and start Git (02:42)

**What:** made the empty folder `~/Desktop/nodus` and ran `git init -b main` in it.
Git identity is `hey-shiv`, `shivashant.personal@gmail.com`.

**Why:** Git records every change with a timestamp. That history is what proves the
work happened during the event, and it gives me save points to roll back to.

**First principles: what `git init` does.**
It creates a hidden `.git/` folder. That folder *is* the repository: every saved
snapshot (a "commit"), with its author, time and parent snapshot, lives there. The
files you see are just the "working tree", your current view. `-b main` names the
first branch `main` instead of the older default `master`. Nothing is saved until the
first commit.

**Q&A:** none yet.

---

## Step 2: `.gitignore` before anything else (02:44)

**What:** wrote `.gitignore` as the very first file. It ignores `.venv/`, `.env`,
`__pycache__/`, `.pytest_cache/` and `.DS_Store`.

**Why:** if a secret (like an LLM API key in `.env`) is committed even once, it lives in
the Git history forever, even after you delete the file, and the repo will be public.
Ignoring it *before* it exists means it can never be committed by accident.

**First principles: how `.gitignore` works.**
Each line is a pattern. When Git looks for new files to track, it skips anything
matching a pattern. A trailing `/` means "a folder". It only affects files Git isn't
tracking yet; a file that's already committed stays tracked, which is exactly why it
has to come first.

What each line is for:
- `.venv/`: the Python virtual environment. Hundreds of MB, machine-specific, and
  rebuilt from `requirements.txt`, so there's no reason to store it.
- `.env`: secrets. Never committed.
- `__pycache__/`, `.pytest_cache/`: files Python and pytest generate to run faster.
- `.DS_Store`: folder-view metadata macOS drops everywhere.

**Q&A:** none yet.

**Open:**
- Should `cache/` (saved LLM replies) be committed? Committing it lets judges replay the
  demo without an API key, but it must then be disclosed. Decided at plan D13.

---

## Step 3: T01, live rules check (02:50)

**What:** fetched the four official pages (brief/FAQ, rules, schedule, resources) and
compared them line by line with the copy I archived on Oct 8. Result written to
`docs/rules-check-2026-10-15.md`: **no material changes**.

**Why:** the organisers said the rules could change before the start. Building for
four days against an outdated rule (say, a new submission field or a data restriction)
would be expensive to discover on Sunday night.

**First principles: why compare against an archive instead of just reading?**
Reading the live page tells you what the rules say *now*. Only a saved earlier copy
tells you what *changed*, and a change is what could invalidate a decision already made
(concept, tracks, deployment). So the check is a diff, not a read.

**What the rules mean for how I build (worth remembering):**
- FalkorDB must do the central work. Test: if the product still works with FalkorDB
  removed, it doesn't qualify.
- AI assistants are allowed, but projects "entirely AI-generated, without meaningful
  participant contribution, verification, or technical understanding" may be rejected.
  That's the reason for this diary and for me writing the brief, blueprint and tests.
- The README must include the graph data model and the Cypher queries.

**Q&A:** none yet.

**Open:**
- Discord announcements need my login. I check them by hand (kickoff? form fields?).

---

## Step 4: The gate becomes an exercise (02:55)

**What:** the plan (and my learning rule) says I write the brief, what NODUS is, in my
own words before any code, and Claude reviews it live. I've used half my weekly Claude
limit, so the live back-and-forth was replaced: the brief is now an exercise in
`00-brief.md` with a hidden answer key, and every later step adds exercises to
`EXERCISES.md`.

**Why:** the rules can reject projects built without real understanding, so I still
need to be able to explain everything. Self-tests with answer keys cost no Claude usage
and I can do them any time (on breaks, at the end of the day).

**Q&A:**
- **Q (me): Can we skip the interactive questions to save usage?**
  A: Yes. Claude keeps building and writes each step's questions into the diary as exercises.

**Open:**
- Do `00-brief.md` (10 min) before the end of day 1.

---

## Step 5: T03, the repo "paperwork" before any code (02:58)

**What:** created the files the rules and the plan need from minute one:

| File | What it's for |
|---|---|
| `README.md` | What NODUS is. Will grow into setup + graph model + Cypher (required by the rules). |
| `AI_USE.md` | The required disclosure of AI-assistant use, and how I review its output. |
| `DATA.md` | Proves the data is allowed: synthetic company + public post-mortems only. |
| `LICENSE` | MIT: anyone may reuse the code with attribution. Without a licence, nobody legally can. |
| `CLAUDE.md` | Rules Claude Code reads at the start of every session (the project's invariants). |
| `docs/decisions/ADR-001`, `ADR-002` | The first two decisions: the concept, and solo + Lite path. |
| `docs/explain-back/`, `eval/` | Placeholders the plan expects; explain-back points to this diary. |
| `docs/rules-check-2026-10-15.md` | The T01 result. |

**Why:** disclosures written on day 1 are honest by construction. Written on Sunday
night, they'd be a guess. And they show judges the process was planned, not patched.

**First principles: what's an ADR?**
An Architecture Decision Record is a short note per decision: what was decided, the
context, the alternatives, why, and the trade-off. Code shows *what* was built; ADRs
keep *why*, which is what judges ask about and what you forget by day 3.

**First principles: what does `CLAUDE.md` do?**
Claude Code automatically loads a file named `CLAUDE.md` from the project folder into
every session. Putting the invariants there ("the LLM never decides matches", "every
query uses parameters") means each new session follows them without being told again.

**Q&A:** none.

---

## Step 6: T04, the Python environment (03:00)

**What:** created a Python 3.12 virtual environment in `.venv/` and installed the
minimal set: `falkordb` (database client), `streamlit` (the app UI), `pytest` (tests),
`pydantic` (validated data shapes), `python-dotenv` (reads `.env`). Pinned every exact
version into `requirements.txt` with `pip freeze`.

**Why:**
- **venv:** keeps this project's packages separate from every other project on the
  Mac, so versions can't clash.
- **Pinning:** a judge who installs in a month gets the exact versions I tested. Without
  pins, `pip` installs whatever is newest that day, and a changed library can break the demo.
- **No LLM SDK yet:** which provider (Gemini free tier, Groq, local Ollama) is decision
  D13. Adding a package before deciding is how projects collect dead dependencies.

**First principles: what a venv actually is.**
A folder holding a link to a Python interpreter plus its own `site-packages/` folder,
where `pip` puts libraries. Running `.venv/bin/python` (or `source .venv/bin/activate`,
which puts `.venv/bin` first on your PATH) makes Python look in that folder for imports.
Nothing magic: it's a separate shelf of libraries.

**First principles: `pip freeze` vs what I asked for.**
I asked for 5 packages, but `requirements.txt` lists dozens. Each package depends on
others (Streamlit alone pulls in pandas, numpy, pyarrow…). `freeze` pins *all* of them,
because a change in any dependency can break things just as badly.

**Q&A:** none.

**Problem and fix (during step 6):**
- **Symptom:** `pip install` sat for 5+ minutes with only `pip` itself installed, no error.
- **Cause:** a slow connection plus big packages (Streamlit pulls in `pyarrow`,
  `pandas`, `numpy`); pip downloads one file at a time and prints nothing with `-q`.
- **Fix:** stopped pip and used `uv pip install`, which downloads in parallel and
  reuses a cache in `~/.cache/uv`. It finished (45 packages pinned).
- **How to spot it next time:** check whether files are appearing in
  `.venv/lib/python3.12/site-packages/`. Growing means slow; frozen means stuck.

**Pinned core versions:** falkordb 1.8.0, redis 8.1.0 (FalkorDB's client talks over the
Redis protocol), streamlit 1.66.0, pytest 9.1.1, pydantic 2.14.1, python-dotenv 1.2.4.

---

## Step 7: First commit (local) (02:59)

**What:** first commit of the skeleton, the diary and `requirements.txt`. Not pushed
yet: creating the public GitHub repo is an outward action that needs my OK.

**Why:** the first commit's timestamp (after 12:01 AM IST Oct 15) is the proof for rule 8.

Pushed to the public repo https://github.com/hey-shiv/nodus (03:02).

---

## Step 8: T05, FalkorDB up, pinned and persistent (03:01)

**What:**
1. Checked Docker Hub: `6.0.2` is still the newest stable FalkorDB tag (`latest` has the
   same digest; the `edge` tags are nightly builds, not stable).
2. Pulled it and confirmed it's a native **arm64** image (no slow emulation on my Mac).
3. Wrote `compose.yaml`: one service, the image pinned by tag *and* digest, both ports
   bound to `127.0.0.1`, a named volume `nodus-data` at `/var/lib/falkordb/data`.
4. Started it, created one test node, stopped and restarted the stack, and the node was
   still there. Then deleted the test graph. Evidence in `docs/g1-lab.md`.
5. Added start/stop/reset commands to the README, with the warning about `down -v`.

**Why each choice:**
- **Pin tag + digest:** a tag like `6.0.2` *can* be re-pushed by the publisher; a digest
  (`sha256:…`) is a fingerprint of the exact bytes and can't change. Judges get the same database I tested.
- **`127.0.0.1:` in ports:** without it, Docker listens on every network interface, so
  anyone on the same café Wi-Fi could reach a database with no password. With it, only my Mac can.
- **Named volume:** a container's own filesystem is thrown away when the container is
  removed. The volume is storage Docker keeps separately, so data outlives the container.
- **Persistence test:** "it should persist" is a belief; restarting and finding the node is evidence.

**First principles: image vs container vs volume.**
- **Image:** a read-only template, a snapshot of a filesystem with FalkorDB installed. Like a class.
- **Container:** a running instance of the image, with a thin writable layer on top. Like
  an object. Remove it and that writable layer is gone.
- **Volume:** a folder Docker manages outside any container, mounted into it at a path.
  The data lives here, so it survives the container being removed and recreated.
- **Compose:** a YAML file describing containers, ports and volumes, so `docker compose up`
  recreates the whole setup the same way every time instead of a long `docker run` command.

**First principles: how did the node survive?**
FalkorDB runs inside Redis, which keeps everything in memory (fast) and saves a
snapshot file, `dump.rdb`, to the data folder. On a clean stop Redis writes that
snapshot; on start it loads it back. The volume is what kept `dump.rdb` between the two containers.

**Findings (things I didn't expect):**
- Only snapshots are on (`appendonly no`). A *crash* loses writes since the last snapshot.
  A clean `docker compose down` is safe.
- The default **query timeout is 1 second**. Slow queries fail instead of hanging, which
  shapes how matching queries get written.
- Two old learning containers exist (stopped), from practice. They're not used and they
  hold no NODUS data. Stopped containers don't take the ports.

**Q&A:**
- **Q (me): Create the public repo and push?** A: Yes → `hey-shiv/nodus`.

**Open:**
- Turn on AOF (append-only file) if crash safety for recorded outcomes matters? Decide at G4.

---

## Step 9: T06, the tiny-graph lab (03:03)

**What:** wrote `tests/test_lab.py`, 12 small pytest tests that each check *one*
FalkorDB behaviour NODUS will depend on, on a 2–5 node toy graph. A pytest **fixture**
(`tests/conftest.py`) gives each test a fresh graph with a random name and deletes it
afterwards. All 12 pass. Saved the EXPLAIN plans and a findings table to `docs/g1-lab.md`.
Recorded the time decision as ADR-003.

**Why:** the whole engine is "count how many conditions of a lesson a plan meets". If
FalkorDB counts or negates differently from what I assume, every match is silently
wrong, and nothing would crash to warn me. Ten minutes of tiny tests now beats a day
of debugging matching later. The tests also stay in the repo as evidence for judges.

**The headline finding:**
`MATCH (a)-[:R]->(b) RETURN count(*)` over **two** parallel edges returns **1**. Name
the relationship (`[r:R]`, `count(r)`) and it returns 2. The EXPLAIN plan shows why:
unnamed, FalkorDB only checks that the nodes are *connected*; named, it walks each
*edge*. Rule for NODUS: **always name relationships when counting**.

**First principles: what's a pytest fixture?**
A function marked `@pytest.fixture` that prepares something a test needs. A test asks
for it just by having a parameter with the same name (`def test_x(graph):`). The code
before `yield` runs before the test (create the graph); the code after runs afterwards,
even if the test failed (delete it). So every test starts clean and leaves nothing behind.

**First principles: what's EXPLAIN?**
A database turns your Cypher into a *plan*: a tree of small steps (scan nodes with a
label, filter, traverse an edge, aggregate). EXPLAIN shows that tree without running it.
Read it bottom-up. It shows *how* the query will run, which is how you spot a wrong count
before it happens.

**First principles: why absence works as "Anti Semi Apply".**
For each `Plan` node, FalkorDB tries the inner pattern ("has an owner?"). *Semi apply*
keeps the row if the inner pattern finds at least one match; *Anti* semi apply keeps it
if it finds **none**. That's exactly "this plan has no owner": a silence condition.

**First principles: why reusing a variable gives consistent bindings.**
In `MATCH (p)-[:OWNS]->(), (p)-[:APPROVES]->()`, both patterns use `p`, so they must
be the *same* node. Only Alice (who owns *and* approves) matches; Bob, who only approves,
doesn't. For NODUS, this is how "the person who ships the change is also the one who
approves it" stays one person across conditions.

**Q&A:** none.

**Open:**
- Indexes on `id` properties: add when the loader exists (T12).

---

## Step 10: T07, graph model v1 (03:08)

**What:** designed the graph model in `docs/graph-model.md` (decision: ADR-004).
1. Listed every condition of the Lite-path lessons: Antibody 1 (5 conditions), Antibody 2
   (4 conditions) and the internal lesson.
2. For each condition, wrote down the relationship it needs.
3. Kept only node kinds and relationships that some condition (or witness rule) needs.
4. Wrote each condition as a Cypher sketch and **ran them all** on a tiny hand-made hero
   plan: 4 of 5 for Antibody 1, 3 of 4 for Antibody 2, with only the completion step missing.

**Why "conditions first"?** The tempting move is to model "a company" (teams, docs,
tickets, Slack) and hope lessons fit. That produces a big graph where most of it does
nothing: the "decoration" the rules warn about. Starting from the conditions means every
relationship does work in a query, and the model stays small enough to build in 4 days.

**First principles: nodes, relationships, properties, labels.**
- A **node** is a thing (a plan, a person). Its **label** (`Plan`) says what kind of thing.
- A **relationship** is a directed, typed connection (`(Plan)-[:TARGETS]->(System)`).
- **Properties** are key–value facts stored on either (`risk_class: 'routine'`).
- Rule of thumb: if you'll ever need to *follow* it, or ask "who/what else connects to
  this?", make it a relationship. If it's a plain attribute you filter on, make it a property.
  That's why "the channel the alerts go to" is a relationship (A2.3 needs to ask "who
  watches *this* channel?"), but "routine" is a property.

**First principles: the three layers.**
- **World:** the company itself (synthetic): plans, systems, channels, people.
- **Lessons:** the immune memory's definitions, stored *in the graph too*, so FalkorDB is
  the system of record and each condition can link to the document sentence it cites.
- **Echoes:** what the agent found and what happened next (its memory). Built later (T22–T23).

**First principles: the anchor (plan D08).**
Every match starts from one plan, the anchor. Each condition is a small query that takes
the anchor's id as a parameter. When one condition finds something another needs (the
staged-rollout procedure, the alert channel), its id is passed along as a parameter
too. That guarantees "the channel" in condition 3 is the same channel as in condition 1.

**First principles: why the hero scores n−1.**
The hero plan is routine, skips the staged procedure others follow, has one automated
gate, and its alerts go to an unwatched email list. It has **not yet** added a rollout
step to all servers. That missing step is the completion condition, so NODUS can say:
*"this plan is one step away from a known disaster, and the step is: rolling out to everything at once."*

**Problem and fix:**
- **Symptom:** `RETURN NOT (p)-[:FOLLOWS]->(...)` failed: "Type mismatch: expected Boolean or Null but was List".
- **Cause:** outside `WHERE`, a pattern means "the list of matching paths", not true/false.
- **Fix:** use `WHERE NOT (pattern)` to filter rows, or `size([pattern comprehension]) = 0` to get a boolean.
- **How to spot it next time:** "expected Boolean … but was List" means a pattern is being used as a value.
- A leftover `lab_` graph from the crashed script was deleted. Scratch scripts now delete in `finally:`.

**Q&A:**
- **Q (me): Draft the model from the plan's B2 needs, explain it, add exercises.** A: Done, in this step.

**Open:**
- Exact condition wording and source sentences: T14 (internal) and T16 (antibodies).
- Condition *kinds* and the compiler that turns them into queries: T08.

---

## Step 11: T08, condition kinds and the compiler design (03:11)

**What:** designed how a lesson becomes runnable queries, in `docs/condition-kinds.md` (ADR-005):
- five **condition kinds**: `present`, `absent`, `attribute_equals`, `count_equals`, `time_order`;
- one shared **spec** vocabulary: `start` (anchor / bound role / "other plans"), `path`
  (1–2 hops), `target`, optional `bind`;
- the **anchor-first evaluator** and its status rules (full / foresight / strong / partial);
- **edge cases decided up front**: no candidate, two candidates, the binding trap,
  parallel edges, missing data vs real absence.
Mapped all 9 Lite antibody conditions onto a kind, with no exceptions.

**Why:** if the LLM wrote a query per lesson, I couldn't vouch for any match, and a
wrong query fails silently. With a fixed set of templates, there are only five query
shapes to understand and test, and every lesson is just data that plugs into them.
The rules (understand your code) and the invariant (the LLM never decides matches) both point here.

**First principles: why identifiers can't be parameters.**
In Cypher, *values* can be `$parameters` (`WHERE p.id = $plan`); the database plans the
query once and plugs values in safely. *Identifiers* (labels like `Plan`, relationship
types like `FOLLOWS`, property names) shape the plan itself, so they must be in the query
text. Pasting text from a lesson into a query is how injection happens. So the compiler
only allows identifiers from the graph model's whitelist, and everything else is rejected.

**First principles: why the compiler is "deterministic".**
Same lesson + same graph → same queries → same answer, every time. No randomness, no
model in the loop. That makes it testable: a pytest can assert exact k values.

**Decisions that differ from the plan (and why):**
- "scope = all" isn't a separate kind; it's `present` with a filter. One less template.
- Added `count_equals`: "the *only* gate" is a count, and `present` can't express "exactly one".
- `time_order` is designed but not built until a lesson needs it.

**Check made:** FalkorDB 6.0.2 rejects maps as property values ("Property values can only
be of primitive types or arrays of primitive types"), but arrays work. So a condition's
`spec` is stored as a JSON string.

**Q&A:** none.

**Open:**
- Does the internal lesson (T14) need `time_order`? If not, it stays unbuilt.

---

## Step 12: T09, the matching prototype, test-first (03:15) → G1

**What:** built the heart of NODUS, three small modules, each with one job:

| Module | Its one job |
|---|---|
| `nodus/schema.py` | Lists the allowed labels, relationship types and property names (the whitelist). |
| `nodus/compiler.py` | Turns one condition (data) into one parameterized Cypher query. |
| `nodus/matcher.py` | Runs a lesson's conditions for one anchor plan, in order, and counts k of n. |

Plus `pyproject.toml` (so pytest can import `nodus`) and `tests/test_matching.py`
(12 tests). Wrote the tests **first**, watched them fail (red), wrote the code, watched
them pass (green). 24/24 tests pass. G1 is passed except the Codex review (`docs/g1-lab.md`).

**Why test-first:** the tests *are* the spec. "Hero = 4 of 5, foresight, missing A1.5" is
written down before any code exists, so the code can't quietly redefine success. A
failing test first also proves the test can fail; a test that never fails proves nothing.

**How the code works (read along in the files):**
1. `evaluate(graph, anchor, lesson)` first checks the anchor plan exists.
2. `_run` takes the first condition. If it needs a role (`role:ch`) that isn't bound
   yet, it's marked `unbound` (counts as not holding).
3. Otherwise `compile_condition` builds the query: `_start` makes the start node
   (`anchor`, `role:x`, or `other:Label`), `_path` adds 1–2 named hops (`r1`, `r2`) and
   target filters, and each kind adds its RETURN. Every value goes into `params`; every
   name is checked against `schema.py`.
4. The query runs with `ro_query` (read-only). It always returns `holds` and `ids`.
5. If the condition binds a role (`bind: "ch"`) and found several candidates, `_run`
   tries the rest of the lesson once per candidate and keeps the best k.
6. `_status` turns k, n and the missing list into full / foresight / strong / partial.

**First principles: red → green → refactor.**
Red: write a test for behaviour that doesn't exist; it fails. Green: write the least code
that makes it pass. Refactor: tidy up while the tests stay green. Each green run is a save
point: if a later change breaks something, a test turns red and points at it.

**First principles: recursion for the "two candidates" case.**
`_run` handles one condition, then calls itself on the rest of the list. When a binder
finds two channels, it calls itself twice (once with each channel bound) and compares
the results. Each call is a smaller version of the same problem, ending when the list is empty.

**Problems and fixes:**
- **pytest couldn't import `nodus`** (expected at the red step). Fix: `pythonpath = ["."]`
  in `pyproject.toml`.
- **Unknown anchor crashed** with `IndexError`: a query on a missing node returns *zero
  rows*, and the code assumed one. Fix: no rows → doesn't hold.
- **Unknown anchor scored k = 1:** A1.2 is a company-level fact, true whatever the plan.
  Fix: `evaluate` checks the anchor exists before evaluating anything. Found by writing
  the test before trusting the code.

**Q&A:** none.

**Open:**
- **Codex review** of T06–T09 (the plan asks for an independent review of ★ cards).
- Lessons are test data for now; storing and loading them from FalkorDB comes at T14–T17.

---

## Step 13: T10, day-1 review (03:20)

**What:** G1 marked passed (`docs/g1-lab.md`). Confirmed the **Lite path** (ADR-006).
Decided the LLM's role (ADR-007): optional, used only for lesson *drafts*; all wording
shown to users comes from templates filled with match results; demo lessons are
hand-authored and pass the same checks an AI draft would.

**Why:** G1 finished early, so the plan allowed Full. But with five prep days skipped,
the margin is worth more as correctness and explanation than as extras. And because no
money can be spent and no local model is installed, the product must run with zero keys.

**First principles: why templates instead of AI wording for heads-ups?**
A template like "{plan} has {k} of {n} conditions of '{lesson}'. Missing: {step}" can only
say what the graph found. An AI writing free text might say something the evidence
doesn't support, and a heads-up that overstates is worse than none.

**Q&A:**
- **Q (me): Keep building, I want the entire end-to-end project.** A: Building every
  Lite card through T35. The video (T36) and the submission (T38) need me.

**Open:**
- Want live AI drafts later? Install a small Ollama model (a download, ask first) or set a free-tier key.

---

## Step 14: T11, the synthetic world (03:23)

**What:** invented a fictional company, **Tern & Tally Freight** (`docs/world-story.md`),
and wrote `nodus/world.py`, which generates it as plain data: 86 nodes and 145
relationships, every node marked `origin: synthetic` with a `source`. The core is designed
by hand (5 current plans, 2 past episodes, people, systems, channels). A **seed** drives 12
background plans that all followed the staged procedure. 7 tests in `tests/test_world.py`.

| Plan | Demo role | Why it exists |
|---|---|---|
| Refresh tariff tables for every depot | hero | echoes 2 public antibodies + the internal lesson, one step away |
| Swap map tile provider | internal echo | matches only the company's own lesson |
| Global rollout of dock sensor content update | control | *sounds* like CrowdStrike, isn't shaped like it |
| Scanner handheld OS patch | near-miss | 3 of 5: close, but not raised |
| Billing report column rename | clean | nothing |

**Why each choice:**
- **Designed, not random, core:** each plan exists to prove one claim (an "aww" moment
  or an evaluation family). Random plans wouldn't reliably contain the shapes.
- **The hero shares no key terms** with the public post-mortems (a test checks this)
  and **the control shares many**: that's the whole argument. Text search should flag the
  control and miss the hero; NODUS does the opposite.
- **Background plans that followed the procedure:** A1.2 needs "other changes use staged
  rollout" to be a *fact in the graph*, not an assumption.

**First principles: what a seed does.**
A computer's "random" numbers come from a formula that starts from one number, the seed.
Same seed → same sequence → same world, every run. Tests can then expect exact counts,
and a judge running the project gets the identical world.

**Q&A:**
- **Q (me): No local model is available, any solution?**
  A: Free options: a local Ollama model (offline, no key), or a free Gemini/Groq key. I asked
  for keys from 6–7 Google accounts, rotated as each runs out, then a strong local model.
  Claude's answer: local **Gemma 4 12B (QAT, 7.2 GB)** is downloading, the strongest that fits
  16 GB next to Docker and the app; Gemini is supported with **one** key in `.env`, falling back
  to local Gemma when the quota ends. Rotating across many accounts wasn't built: Google's API
  terms prohibit creating multiple accounts to get around usage limits, and a ban mid-event
  would cost more than the quota. API keys go in `.env` (gitignored), never into a chat.

---

## Step 15: T12, the loader (03:26) → G2

**What:** `nodus/db.py` (one place that knows how to connect) and `nodus/loader.py`:
nodes are grouped by label and written with `UNWIND $rows … MERGE (n:Label {id: row.id})
SET n += row.props`; relationships are grouped by (type, from-label, to-label), and both
endpoints are `MATCH`ed before `MERGE`ing the relationship. Every label's `id` gets an index.
Tests: the loaded counts equal the generator's own counts, and **loading twice changes nothing**.
G2 passed.

**Why:**
- **`MERGE` instead of `CREATE`:** `CREATE` always adds; run the loader twice and you'd have
  two of everything, and every count (k of n!) would double. `MERGE` means "find it by id,
  create it only if missing", so the loader can run any number of times (idempotent).
- **`UNWIND` a list:** one query per label with all rows as a parameter, instead of one
  query per node. Fewer round trips, and values stay parameters.
- **MATCH endpoints, then MERGE the relationship:** `MERGE (a:Plan {id:…})-[:X]->(b…)` in one
  pattern would create *new* endpoint nodes whenever the full pattern isn't found. Matching
  first guarantees the relationship attaches to the existing nodes.
- **Index on `id`:** without it, every `MERGE`/`MATCH` by id scans every node of that label.

**Problem and fix:**
- **Symptom:** "Invalid graph operation on empty key" on the first load.
- **Cause:** listing a graph's indexes fails when the graph doesn't exist yet.
- **Fix:** just `CREATE INDEX`, and treat FalkorDB's "already indexed" error as fine.
- **How to spot it next time:** "empty key" means the graph hasn't been created yet.

**Q&A:** none.

**Correction (03:37):** the times on steps 7–15 were first written as estimates and ran
ahead of the clock. They've been corrected to the real git commit times. From here on,
every time is read from the clock.

---

## Step 16: T13, the internal post-mortems (03:30)

**What:** wrote two synthetic post-mortems in `data/postmortems/`: E1 (label printer
firmware push, the source of the internal lesson) and E2 (invoice export review, a
near-incident where the concern was *accepted*). Both are blameless and marked synthetic.
Each sentence the internal lesson needs is written as a plain, explicit sentence.

**Why:** a lesson condition is only as trustworthy as the sentence it cites. "Nobody was
watching the printer-alerts email list" can be checked; "communication issues" can't.

**First principles: blameless wording.**
A post-mortem that blames people makes them hide information next time. Blameless
format describes systems and decisions ("the request was declined to keep the release on
schedule"), not fault ("X ignored Y"). It matters doubly for NODUS: the witness feature
invites the person who raised a concern, which must read as *asking for advice*, never as
"who was right". So the concern is recorded as a fact, with no verdict.

---

## Step 17: T16 (first), primary-source quotes for the antibodies (03:30)

**What:** for each public incident I downloaded the organisation's own published page
(Cloudflare's post-mortem, CrowdStrike's review hub, the SEC press release on Knight
Capital, GitLab's post-mortem) and checked every quote **character for character**
against the page text. 19/19 quotes across the three lessons are verified.
`scripts/verify_sources.py` repeats this check for anyone. The page texts are cached
locally in `cache/sources/` (gitignored: NODUS cites these pages, it doesn't redistribute them).

**Why:** the antibodies name real companies. One misquote and the whole project's
credibility goes. A summary tool also *paraphrases*: the first pass used a web tool
that summarises pages, so its "quotes" couldn't be trusted until checked against the raw text.

**Findings while verifying:**
- CrowdStrike's review doesn't say the update went "to every host at once" (that was a
  secondary-source claim in my plan). It says the update was published to Windows hosts
  running sensor 7.11+, and the fix is a *staggered deployment starting with a canary*. So
  the CrowdStrike citation on A1.3 is marked as "remediation step; implies no staggered
  deployment before", and A1.5 ("goes to every target at once") cites only Cloudflare's
  "went global in seconds".
- The Knight "97 automated emails" fact is in the SEC press release itself (not only in secondary summaries).

**Decision: `cache/` is gitignored** (closes the open question from step 2): fetched
pages are cited, not redistributed, and LLM replies are a local convenience.

---

## Step 18: T14 + T16, lessons as validated data (03:33)

**What:**
- `data/lessons/`: three hand-authored lessons as JSON: Antibody 1 (Cloudflare 2019 +
  CrowdStrike 2024), Antibody 2 (Knight 2012 + GitLab 2017), internal "The quiet push" (E1).
  Each condition has a kind, a spec, plain text and at least one verbatim citation.
- `nodus/lessons.py`: pydantic models; three checks a lesson must pass (shape, compiles
  against the whitelist, quotes verbatim); storage in FalkorDB as `Lesson`, `Condition`,
  `CITES {quote}`, `LEARNED_FROM`; `approve()`, with versioning (an edit creates a new
  version that needs approval again); `active_lessons()` reads approved lessons back from the graph.
- `nodus/llm.py`: one call that returns JSON. It tries Gemini (if a key is in `.env`), then
  the local Gemma model, and caches every reply on disk.
- `nodus/proposals.py`: the LLM drafts a lesson from a post-mortem; the draft is retried
  with the problems listed, up to 2 times, then quarantined. Even an accepted draft is only *proposed*.
- Tests: 11 for lessons, 6 for proposals (fake LLM, no real calls).

**Why the LLM is boxed in like this:** it's good at reading a post-mortem and suggesting
a shape, and bad at being exactly right. So it never writes queries (the compiler does),
can't invent evidence (the verbatim check rejects it), and can't activate anything (only
`approve()` does, and only a human calls it).

**First principles: pydantic.**
You describe the data's shape as a Python class (`kind` must be one of four strings,
`conditions` must have 3–6 items...). `Lesson.model_validate(data)` either returns a typed
object or raises an error that lists what's wrong. It's a gate at the boundary: anything past
it has the right shape.

**First principles: a fallback chain.**
Try the best option; if it fails (quota, offline), try the next. The caller asks once and
doesn't care which provider answered. The cache sits in front: the same prompt never costs twice.

**Problem and fix:**
- **Symptom:** "Invalid graph operation on empty key" when storing the first lesson.
- **Cause:** the same FalkorDB behaviour as in step 15: reads fail on a graph that was never written.
- **Fix:** one helper, `nodus.db.read()`, treats that error as "no rows". Lessons and the matcher use it.

---

## Step 19: T17, matching the whole world (03:35) → G3

**What:** `nodus/watch.py` runs every approved lesson over every current plan:
- stage 1 (cheap): skip lessons whose anchor relationships the plan doesn't have at all;
- stage 2 (careful): the anchor-first evaluator.
An echo is **raised** when k ≥ n − 1. `scripts/setup_demo.py` rebuilds the demo graph
(world + lessons). `tests/test_g3.py` turns the designed expectations into 7 tests, all
green on the first run. The results table is in `docs/g3-results.md`. 55/55 tests pass.

| Plan | Result |
|---|---|
| hero | **foresight** on all three lessons: 4/5, 3/4, 4/5, missing only each completion step |
| maps (internal echo) | **full** on the internal lesson, and on Antibody 2 (its alerts also go nowhere) |
| sensor (control) | nothing raised (2/5, 2/4, 3/5), despite sharing CrowdStrike's words |
| scanner (near-miss) | 3/5, not raised |
| billing (clean) | nothing raised |

**Why the control stays quiet:** it *says* "global rollout", "content update", "validator",
"channel file". But structurally it follows the canary procedure (A1.3 fails), has a human
review (A1.4 fails) and pages a watched on-call (A2.2 and A2.3 fail). NODUS never reads the
words; it checks the relationships.

**First principles: why the maps plan matched Antibody 2 too.**
I designed it as the "internal echo", but its alerts go to an unwatched email list and it
goes live, which is exactly Knight's and GitLab's shape. I didn't hide that: one plan can
echo several lessons, and here the extra echo is correct.

**Q&A:** none.

**Open:**
- Gemma 4 download still running; Gemini needs a key in `.env` (optional).
- The CrowdStrike/A1.3 citation is an inference from a remediation step: say so on the Echo page.

---

## Step 20: LLM keys and model selection (03:42)

**Q&A:**
- **Q (me): How and where do I get the API keys, and is there a model selection procedure?**
  A: Gemini key: aistudio.google.com/apikey → *Create API key* → copy it into `.env` as
  `GEMINI_API_KEY=` (start from `.env.example`). Don't add billing, so nothing can be charged.
  Never paste a key into a chat or commit it. Check with `scripts/llm_check.py`, which lists the
  models the key can use and tests each one without printing the key.
  Selection: Gemini first (if a key is set), trying `gemini-3.8-flash` then
  `gemini-3.5-flash-lite` (checked against Google's model list today; the old default 2.5 Flash
  is now limited to existing users), then local `gemma4:12b-it-qat`. Change the order with
  `NODUS_GEMINI_MODELS` in `.env`.

**First principles: why the key lives in `.env`.**
A key is a password for a paid service. Code is public; `.env` is local and gitignored.
`python-dotenv` reads `.env` into environment variables when the program starts, so the
code asks for `os.environ["GEMINI_API_KEY"]` and the key itself never appears in the repo.

---

## Step 21: T19–T23, severity, silence, witnesses, the agent loop, memory (03:40)

**What:**
| Module | Its one job |
|---|---|
| `nodus/severity.py` | k, n and the missing list → full / foresight / strong / note / ignore (a pure function, the B6 table) |
| `nodus/wording.py` | Fills sentence templates from match results; absences say "Not recorded in the company graph" |
| `nodus/witnesses.py` | Whom to invite, by B8's rules in order; public lessons return their sources, never people |
| `nodus/agent.py` | `on_plan_saved`: match → decide → heads-up + invitation → remember as an Echo; `acknowledge`; `track_record`; `inbox` |

24 new tests (79 total, all green). On the demo world, saving the hero plan raises three
**foresight** echoes. The internal one invites **Asha Rao** (she asked for a canary batch
last time and was overruled). The public ones cite Cloudflare/CrowdStrike and Knight/GitLab.
The silence lines read: *"∅ Not recorded in the company graph: nobody active is watching
that channel ("tariff-errors@ list")"* and *"…an active owner for "tariff-errors@ list""*.

**Why it's an agent, not a script:** it acts on connected data (the graph decides), it
chooses whom to involve (witness routing walks lesson → episode → concern → person), and it
**remembers**: each echo is a record with a stable id (`echo:<lesson>:<plan>`). Saving the
plan again updates the same record (`times_seen` goes up). The human's outcome (heeded /
dismissed with a reason / escalated) is kept, and the lesson's track record is counted from those outcomes.

**Where the human decides:** approving a lesson; acknowledging an echo. The agent never
edits a plan, never approves anything, never sends a message.

**First principles: a pure function.**
`level(k, n, missing, completion)` uses only its inputs: no database, no clock, no
screen. Same inputs, same answer, forever. That makes it trivially testable (one test per
table row) and it's why severity is a published *rule*, not an AI's opinion.

**First principles: why graph distance isn't expertise.**
"Closest person in the graph" sounds clever but means nothing: someone two hops away may
just share a team. NODUS invites by *role in the original episode* (who warned, who wrote the
post-mortem, who owns the system), which is a reason a human can read and agree with.
Witnesses are never scored or shown as "who was right".

**Design decisions:**
- "Exactly half" counts as a *note* (`NOTE_SHARE = 0.5`), chosen on the demo world only.
- When a plan is fixed so it no longer echoes, its old echo is kept and marked **cleared**
  (memory isn't deleted).
- The "no owner" silence is a *supporting* observation: it's shown, but it isn't a lesson
  condition and doesn't change k.

**Q&A:** see step 20.

---

## Step 22: T24–T28, the Streamlit app, and the end-to-end path (03:48) → G4

**What:** a five-page app (`streamlit run app.py`):
| Page | What it does |
|---|---|
| Plans | A ledger of plans, each lesson shown as a **shape strip** (one dot per condition, filled when it holds, a dashed red ring for the missing completion step). A form lets the owner edit a plan; **Save** runs the agent. |
| Echo | The alignment picture: the past failure's conditions beside what the plan contains, drawn by `nodus/svg.py` from the match result only. Plus the heads-up, silences, witness and every source sentence. |
| Inbox | "Viewing as" a person: heads-ups on plans they own, invitations as a witness; the owner records heeded / dismissed (reason required) / escalated. |
| Lessons | Each condition beside its quote; Approve / Reject; track record; "Draft a lesson" with the LLM (checked before it's stored). |
| How it works | The method and the honest limits, in plain words. |
Supporting modules: `nodus/plans.py` (plan reads and edits), `nodus/view.py` (match → display rows),
`nodus/svg.py` (the pure drawing function), `app_pages/common.py` (cached connection, error guard, CSS).
**No page file contains Cypher** (checked with grep). 86 tests green.

**Clicked through in the browser (G4):** reset → Plans shows the hero "one step away" on all
three lessons → added "rollout to every target" and saved → all three became **full** → Inbox
(as Lena) showed the heads-ups with silences → recorded "Change the plan" → Lessons showed the
track record "raised 1, heeded 1". The raw screen recording (plan T28) is for me to make.

**Design choices (from the design pass):** lichen-paper background, slate ink, teal for
"holds", violet for ∅ silence, red *only* for the completion step; one typeface (Atkinson
Hyperlegible, built for legibility); no dashboard cards or KPI tiles. The headline is a plain
sentence: "1 of 5 plans is one step from a known failure."

**First principles: how Streamlit runs a page.**
Every click re-runs the page script from top to bottom. Widgets return their current value
on each run. So: `st.form` groups inputs so nothing happens until **Save** is pressed (no
half-saved plans), `st.session_state` keeps small things between runs (which echo to open),
and `st.cache_resource` keeps *one* database connection instead of reconnecting on every click.

**First principles: why the SVG is a pure function.**
`alignment_svg(lesson_name, plan_title, rows, k, n, level)` only turns rows into text. The
rows come from `rows_for`, which comes from the match. So the picture can't show anything the
graph didn't say, and pytest can check it ("the completion line is dashed red", "it says 4 of 5").

**Problems and fixes:**
- **The sidebar icon showed as the text "_arrow_right":** my font override also replaced
  Streamlit's icon font. Fix: restore *Material Symbols* for icon elements.
- **Edits to modules didn't show up:** Streamlit only reloads files automatically when a file
  watcher is installed; without one, restart the server after editing modules.
- **The step dropdown didn't register automated typing:** replaced it with radio buttons,
  which is also one click instead of three for the demo.

**Q&A:** none.

**Open:**
- **T28 insurance recording:** mine to do (screen recording of the path above).

---

## Step 23: T30–T31, the evaluation (03:52) → G5

**What:**
1. Wrote `eval/DECLARATION.md` (questions, families, metrics, baselines, dev/test split) and
   **committed it at 03:49:55, before any evaluation data existed**.
2. `eval/generate.py` builds the families (seeded) in a separate graph per split;
   `nodus/baseline.py` is the keyword baseline (TF-IDF, pure Python); `eval/run.py` runs both.
3. Ran dev (to fix the baseline threshold), then **test once**. Results in `eval/RESULTS.md`.

**Test results (synthetic):** NODUS: F1 hits 18/18, F2 false alarms 0/18, F4 0/10, F3
foresight 20/20. Keyword baseline at its declared threshold: F1 18/18 but F2 18/18 and F4 10/10
false alarms; at the smallest positive threshold: F1 1/18.

**What it does and doesn't prove:** structure decides and wording doesn't, and the queries
implement the lessons. It does *not* prove real-world accuracy: the families come from the
same condition definitions, and roles are given, not extracted. The embedding baseline (B1)
was not run. All of this is written in RESULTS.md.

**Where NODUS loses:** a trivial footer-year change with the risky shape gets a **full** echo.
Structure can't see stakes. Reported, not hidden.

**First principles: why declare before running?**
If you look at results and *then* decide what to measure, you can (even unknowingly) pick the
measures that make you look good. Writing the questions, metrics and thresholds rule down
first, with a timestamped commit, makes that impossible. Git is the notary.

**First principles: dev/test split.**
Anything you tune (the baseline's threshold) is tuned on dev. Test is touched once, so its
numbers are an honest estimate rather than something you've fitted to.

**Q&A:** none.

---

## Step 24: T33–T35, keyword comparison, README, disclosures (03:59)

**What:**
- **Plans page:** a "Compare with keyword search" table. On the demo plans, keyword search
  ranks the **control** (dock sensor) closest to the CrowdStrike/Cloudflare lesson (0.21), the
  **hero** at 0.07, and the **map tile** plan at 0.00. NODUS raises the hero and the map plan and
  stays quiet on the control. That's storyboard frame 6, built from the same baseline as the evaluation.
- **README:** what it is, why the graph can't be removed, a 5-minute quick start, the graph
  model, the **actual compiled Cypher** for the hero plan, the witness walk, the echo-memory
  query, verified FalkorDB behaviours, evaluation counts with their limits, limitations,
  sources, tracks, disclosures, layout.
- **AI_USE.md / DATA.md:** what the AI may and may not do in the product; the demo lessons were
  hand-authored and passed the same checks; all four public sources with what each is used for.
- **Local Gemma 4 12B** finished downloading and answers through `scripts/llm_check.py`. A real
  draft of the E1 lesson is running in the background.

**Why the README shows compiled queries, not hand-written ones:** the rules ask for "the Cypher
queries the product depends on". Printing what `compile_condition` actually produces means the
README can't drift from the code.

**Q&A:**
- **Q (me): Can we use this model somewhere? https://github.com/NandhaKishorM/laya**
  A: Laya is a classifier (not a chatbot): it answers typed questions about a text, such as
  *choice* (pick a label), *score* or *yes/no*, with a calibrated probability, in one pass. The
  models are 322M–421M-parameter encoders, Apache-2.0, and run on CPU at about 0.2–0.5 s per call.
  The best fit is NODUS's biggest stated limitation: **roles are given, not extracted.**
  Laya could *suggest* a plan's controlled-vocabulary roles from its text (risk class, change
  type, alert channel kind) and categorise dismissal reasons for the learning loop. The guard
  rail: a suggestion is never used for matching until a person confirms it, otherwise words
  would leak back into a structure-only decision (the control plan "sounds" risky). Cost: PyTorch
  plus about 1–2 GB of checkpoints on a slow connection. Recorded as an option for me to decide.

---

## Step 25: Laya, optional role suggestions with a human check (04:08)

**What:**
- `nodus/suggest.py`: an optional wrapper around Laya's `Router.predict` (the API checked in
  its README and PyPI page first; v0.4.7, Apache-2.0). `suggest_roles()` suggests a plan's
  **risk class** and **change type**; `categorise_reason()` guesses a dismissal reason's category.
- Suggestions are stored **beside** the real roles (`Plan.suggested_risk_class` and so on).
  The matcher never reads them. `confirm_role()` (a person's click on **Confirm**) copies a value
  into the real role, and then the agent re-runs.
- UI: *Plans → Suggest roles from the plan's text*; the Inbox sorts dismissal reasons when
  Laya is installed; Lessons shows the guesses, labelled experimental. Decision: ADR-008.
- `requirements-laya.txt` keeps PyTorch and Laya out of the core install. 6 new tests with a
  fake predictor (92 total), including **"a suggestion alone never changes the match"** and
  **"confirming does"**.

**Measured with the real model (honest numbers):**
| Job | Result |
|---|---|
| risk class vs the recorded role, 5 demo plans | 4 of 5 agreed (scanner patch: "standard" instead of "routine") |
| change type, 5 demo plans | 3 of 5 |
| confidence | 0.10–0.33; Laya itself warned this checkpoint's confidence is partly uncalibrated |
| dismissal reasons, 6 labelled examples (choice question) | 2 of 6 (near chance) |
| dismissal reasons, yes/no questions | every answer exactly 0.50, so this question type isn't working with this checkpoint |

**Why the guard rail matters (first principles):** NODUS's whole claim is that *structure,
not words*, decides. Laya reads words. If its guess went straight into `risk_class`, a plan
that merely *sounds* routine could switch on condition A1.1, and the control-plan problem
comes back through the side door. Keeping suggestions in separate properties that no query
reads, plus a confirm step, means words can *propose* and only a person can *decide*. That's
the same rule as for LLM-drafted lessons.

**First principles: a classifier vs a generative model.**
Gemma *writes* text (it can say anything, so its output must be checked). Laya *chooses* from
the options you give it (it can only answer "routine", "standard" or "high") and gives a
probability. That makes it fast and safe to plug into a controlled vocabulary, but it's only as
good as its training, and here its confidence was low.

**Problems and fixes:**
- **The Gemini SDK wasn't actually installed:** the earlier background install "succeeded"
  because the shell pipe's last command (`tail`) succeeded, which hid the real failure.
  Reinstalled (google-genai 2.30.1) and pinned it in `requirements.txt`.
  **How to spot it next time:** check that the import works, not just the exit code.
- **The local Gemma draft timed out (10 min):** Gemma 4 "thinks" before answering, and RAM was
  shared with the Laya install. Fix: `think: false`, an output cap, and a configurable timeout
  (`NODUS_OLLAMA_TIMEOUT`). Retrying.

**Q&A:**
- **Q (me): Add Laya as optional role suggestions that a human must confirm, plus dismissal-reason
  categories, and keep it optional.** A: Done as described. Reason categories are marked
  experimental because they measured near chance.

---

## Step 26: A real AI draft against the checks (04:13)

**What:** ran `propose_lesson` for real, with local **Gemma 4 12B** on the E1 post-mortem.
- **Attempt 1** (thinking on): timed out after 10 minutes.
- **Attempt 2** (`think: false`): 3 drafts in 202 s, all **rejected**. Draft 1 named a completion step
  that wasn't one of its conditions; drafts 2–3 wrote `"all_targets": true` instead of an object.
- **Prompt fix:** added two worked example conditions (toy library domain, shape only) and the
  rule "completion must equal a condition id". New test checks the prompt shows it.
- **Attempt 3:** 3 drafts in 109 s, all **rejected**: each used a role (`role:owner`) before
  any condition had bound it.

**What it means:** the drafts were close (4–5 conditions, sensible kinds, real quotes), but a
12B local model doesn't reliably follow a strict schema with cross-references. **Every bad draft
was caught and quarantined before reaching a human.** That's the safety net working, and
why the demo lessons are hand-authored (disclosed). A stronger model (Gemini, with a key) may
pass; it goes through exactly the same checks.

**First principles: why validation beats trust.**
A model's output is a *proposal*. Pydantic checks the shape; the compiler dry-run checks the
names and role order; the verbatim check catches invented quotes. Each check is cheap,
deterministic and explains its failure, and the explanation is fed back for a retry.

**Q&A:** none.
