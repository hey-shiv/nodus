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

## Step 7: First commit (local)

**What:** first commit of the skeleton, the diary and `requirements.txt`. Not pushed
yet: creating the public GitHub repo is an outward action that needs my OK.

**Why:** the first commit's timestamp (after 12:01 AM IST Oct 15) is the proof for rule 8.
