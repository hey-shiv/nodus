# Learn from mistakes you never made

*Draft for the Graph Hacks blog side prize. Edit it into your own voice before publishing.*

In 2003, the board investigating the loss of the space shuttle Columbia wrote a chapter called
*History as Cause*. The organisational causes of Challenger, seventeen years earlier, had come
back. Different hardware, different people, same shape.

Companies do this all the time, and not because nobody wrote the lesson down. Usually somebody
did. The lesson sits in a post-mortem, waiting to be searched for, and people search by what
things *sound* like. A plan to "refresh tariff tables for every depot" will never surface a
post-mortem about "a rule change that went global", even when it's the same mistake waiting to happen.

So for Graph Hacks I built NODUS, which stores lessons as **shapes** instead of words.

## A lesson is a pattern

Take two famous outages. In 2019, Cloudflare's procedure "allowed a non-emergency rule change
to go globally into production without a staged rollout". In 2024, CrowdStrike content passed a
single validator and, trusting earlier successful deployments, went to production. Strip the
names away and you get the same handful of facts:

- the change is treated as routine;
- the company has a staged rollout procedure that other changes follow;
- this change doesn't follow it;
- one automated check is the only gate;
- it goes to everything at once.

Each of those is a fact about **relationships**: a plan *follows* a procedure (or doesn't), is
*gated by* checks, *has a step* with a scope. That's a graph. In NODUS each lesson is a small set of
these conditions, stored in FalkorDB, and every condition quotes the exact sentence it comes from.

## Matching a shape

When someone saves a plan, NODUS runs one small Cypher query per condition, always starting from
that plan. A condition can be "present", "absent", "a property equals something" or "exactly n of
something". A tiny compiler turns each condition into a parameterized query; no AI writes a query
that runs.

The interesting part is the count. If four of five conditions hold and the missing one is the
*last step* (sending it everywhere at once), NODUS doesn't say "this looks like CrowdStrike". It says:
**you're one step away, and this is the step.** That's foresight rather than hindsight.

Two details mattered more than I expected:

- **Consistent roles.** "The alert channel" in one condition must be the same channel in the next.
  NODUS passes the id found by one query into the next as a parameter.
- **Counting in FalkorDB.** Before relying on anything, I wrote small tests of FalkorDB's behaviour.
  One surprised me: counting over an *unnamed* relationship returned 1 for two parallel edges.
  So every relationship NODUS counts is named. A wrong count would silently give a wrong answer.

## The control plan

The demo company also has a plan called "Global rollout of dock sensor content update". It's
practically made of CrowdStrike vocabulary. Keyword search ranks it closest to that outage. NODUS
raises nothing, because the plan follows the canary procedure, has a human review, and its alerts
page an on-call engineer who's watching. Same words, different shape.

## Remembering, and asking the right person

When the company's own history matches, NODUS invites the person who raised a concern last time,
if it was overruled and they're still around. It goes by their role in the old incident, never by
a score. Every warning becomes a record: what the owner did about it (heeded, dismissed with a
reason, escalated), so each lesson builds a track record over time.

## Did it work?

I wrote the evaluation plan down and committed it *before* generating any test data, then ran the
test split once. On plans with a lesson's structure but none of its words, NODUS raised the right
lesson 18 of 18 times; on plans with a lesson's words but a safe structure, it raised nothing
(0 of 18). A keyword baseline couldn't separate the two.

That's synthetic data built from the same definitions, so it shows the idea works as designed, not
that it's ready for a real company. Real use needs plans to record their roles: risk class, alert
routes, procedures. It also loses in an instructive way. A trivial "update the footer year" change
with the risky shape gets a full warning, because structure can't see stakes. The dismissal
reasons are how the lessons get refined.

## What I learned

I started this hackathon knowing Python and Git, having done one day of a six-day prep plan. Every
step of the build, with what went wrong, is in the repo's diary. The thing I'll keep: **decide what
you'll measure before you look**, and **test the database's behaviour before you trust it**.

Code: https://github.com/hey-shiv/nodus
