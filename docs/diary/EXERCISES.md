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
