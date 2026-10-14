# Submission pack

Everything for the Graph Hacks form, ready to paste. Only two things are left for me:
**record the video** and **fill in the form**. Aim to submit by **8 PM IST, Sun Oct 18**
(closes 11:59 PM IST).

---

## Form answers

**Project name:** NODUS

**Tagline:** Learn from mistakes you never made.

**Short description (under 280 characters):**
> NODUS stores lessons from post-mortems as patterns of roles and relationships in FalkorDB
> and checks every plan against them. When a plan takes the shape of a past failure, it names
> the one step that would complete it and invites the person who warned last time.

**Repository:** https://github.com/hey-shiv/nodus

**Demo video:** *(paste the link after uploading)*

**Deployment:** Local setup (tested from a fresh clone): README "Quick start", about 5 minutes
with Docker and Python 3.12.

**Tracks:** Track 03 Company Brain (primary). Also fits Track 01 (Agents That Act on Connected
Data) and Track 02 (Agent Memory). *My decision at submission: enter 03, and add 01 if the form
allows several without penalty.*

**Long description:**
> Companies repeat failures, including ones they already wrote down, because people and search
> tools look for lessons by what things sound like. NODUS turns lessons from post-mortems (the
> company's own and famous public ones: Cloudflare 2019, CrowdStrike 2024, Knight Capital 2012,
> GitLab 2017) into small patterns of roles and relationships, stored in FalkorDB. Every
> condition quotes the sentence it comes from, checked word for word, and a person approves each
> lesson.
>
> When a plan is saved, an agent checks it against every approved lesson, one small graph query
> per condition, starting from the plan. It counts how many conditions hold. If all but the
> lesson's last step hold, NODUS says the plan is one step away and names that step. It also
> shows what's missing from the record (nobody watching the alerts, no owner), invites the
> person who raised the concern last time (by their role in the old incident, never by a score),
> and remembers what the owner did about it, so each lesson builds a track record.
>
> In the demo, a plan written in completely different words is one step from three past
> failures, while a plan that uses CrowdStrike's own vocabulary but is structured safely raises
> nothing. In a pre-declared synthetic evaluation (test split run once), NODUS raised the right
> lesson for 18 of 18 different-words plans with 0 of 18 false alarms on same-words plans. A
> keyword baseline couldn't separate the two. The README states the limits, including where
> NODUS loses.

**How FalkorDB is used (if asked):**
> FalkorDB is the system of record for everything: the synthetic company (plans, systems, alert
> channels, people, past incidents), the lessons and their cited sources, and the agent's memory
> (echoes, outcomes, track records). A deterministic compiler turns each lesson condition into a
> parameterized Cypher query (present, absent, attribute and count templates); matching is
> read-only (`ro_query`) and anchor-first, so roles stay consistent across conditions. Remove
> FalkorDB and nothing can be matched. The README lists the exact queries and FalkorDB behaviours
> we verified first (for example: counting over an unnamed relationship returns 1 for parallel edges).

**Tech stack:** FalkorDB 6.0.2 (Docker), Python 3.12, Streamlit, pydantic, pytest. Optional:
Gemini (free tier) or local Gemma 4 via Ollama for lesson drafts; Laya for role suggestions.

**AI assistance disclosure:**
> I used Claude Code (Anthropic) to explain concepts, draft code and tests for functions I
> approved, check primary sources, and draft build-diary entries that I reviewed. The concept,
> decisions, scope and evaluation protocol are mine. Every step is logged in docs/diary/ with the
> reasoning, problems and fixes. Inside the product, an AI model may only draft lessons, which
> must pass automatic checks and a human approval; it never writes the queries that run, decides
> a match, or approves anything. Details: AI_USE.md.

---

## Pitches

**30 seconds:**
> Companies keep repeating failures they already wrote down, because we look for lessons by how
> they sound. NODUS stores lessons as graph patterns in FalkorDB: roles and relationships, not
> words. Here's a plan that shares no words with CrowdStrike's outage, and NODUS says it's one
> step away from it, names the step, and invites the engineer who warned about it last year.
> And a plan that sounds exactly like CrowdStrike but is built safely? NODUS stays quiet.

**60 seconds:** the 30-second version, plus:
> Every lesson condition quotes the exact sentence it comes from, and a person approves it. A
> compiler turns conditions into Cypher; no AI writes a query that runs. The agent remembers what
> the team did, so lessons build a track record. In a pre-declared test, it found 18 of 18
> different-words echoes with zero false alarms, where keyword search couldn't tell them apart.

---

## Video script (3:00): click by click

**Before recording:**
1. Docker Desktop running; `docker compose up -d`.
2. `.venv/bin/streamlit run app.py`; browser at http://localhost:8501, window about 1280 × 800, zoom 110%.
3. Sidebar → **Reset the demo** → keep "Lessons already approved" ticked → **Reset demo world**.
4. Quit Ollama and close other apps (memory and notifications). Do a 10-second test recording first.

| Time | Screen | Say (draft; use your own words) |
|---|---|---|
| 0:00–0:15 | Plans page title: "1 of 5 plans is one step from a known failure" | "In 2003, the board investigating Columbia wrote a chapter called *History as Cause*. Companies repeat failures they already wrote down, because we search lessons by how they sound." |
| 0:15–0:35 | Echo page, lesson "The trusted change, everywhere at once"; open **Every condition, with its source sentence** and scroll to the Cloudflare and CrowdStrike quotes | "In 2019 a Cloudflare rule change skipped the staged rollout and went global in seconds. In 2024 a CrowdStrike update passed a single validator and was deployed. Different companies, different words, same shape. Every condition here quotes the published post-mortem." |
| 0:35–0:55 | Plans page, the hero row "Refresh tariff tables for every depot" with its three shape strips | "This is a plan at a synthetic freight company. It doesn't share a keyword with those post-mortems. NODUS checks structure: who and what is connected." |
| 0:55–1:35 | **Open echo** on the hero, Antibody 1: the alignment picture | "Four of five conditions hold: routine, skips the canary procedure others follow, one automated check. The fifth, sending it to every depot at once, isn't in the plan yet. That's the step not to take. The violet mark is a silence: nothing recorded where something should be." |
| 1:35–2:00 | Echo, lesson "The quiet push" → **Who saw it coming** (Asha Rao) | "NODUS also remembers the company's own history. Last year Asha asked for a canary batch before a firmware push and was overruled. She's still here, so NODUS invites her, by her role in that incident, never by a score." |
| 2:00–2:25 | Plans → open **Compare with keyword search** | "And a plan that only sounds like a disaster? Keyword search ranks the dock-sensor plan closest to CrowdStrike. NODUS raises nothing, because that plan follows the canary procedure, has a human review and pages a watched on-call." |
| 2:25–2:45 | Inbox (Lena Brandt) → choose **Change the plan** → **Record my answer**; then Lessons → track record | "The owner records what she'll do. NODUS remembers it, and the lesson's track record updates." |
| 2:45–3:00 | README section "The Cypher NODUS depends on" (or the repo on GitHub) | "Because a lesson is a graph pattern, FalkorDB is where it lives and where it watches. In a pre-declared test: 18 of 18 echoes found, zero false alarms. Learn from mistakes you never made." |

**Optional extra shot** (if time allows): Plans → Change a plan → Add a step: *rollout*, scope
*every target* → **Save plan**. The banner turns to "full": the step not to take, taken.

---

## Final checklist (in order)

- [ ] Gemini key in `.env` (optional) and `scripts/llm_check.py` passes
- [ ] Record the video (OBS or QuickTime), upload (YouTube unlisted or Loom), check it plays logged out
- [ ] Paste the video link into the README ("Demo video" line) and commit
- [ ] Glance at the FalkorDB and WeMakeDevs Discord announcements for any form changes
- [ ] Codex review of `nodus/compiler.py` and `nodus/matcher.py` (plan step for the core cards)
- [ ] Fill in the form with the answers above; name the track(s)
- [ ] Screenshot the confirmation into `docs/` and commit
- [ ] Optional: publish the blog post (`docs/blog-post.md`) for the side prize
