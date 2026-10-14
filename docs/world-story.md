# The synthetic world: Tern & Tally Freight (fictional)

Plan task T11 (decision D12). **Everything here is synthetic.** Tern & Tally Freight, its
people, systems and incidents are invented for the demo. Any resemblance to real people
or companies is unintended. Real companies appear only as cited sources inside the
public antibodies.

## The company in one paragraph
A mid-size freight company. Changes to its systems normally go through a **staged
rollout procedure** (canary batch first, then everyone), and dozens of past changes did.
Alerts from each system go to a channel: the on-call **pager** (watched), a team
**chat** room (watched), or an old **email list** (nobody really reads it). Two years of
incidents left two post-mortems.

## Past episodes (the internal memory)
| Episode | What happened (shape) | Concern | Lesson? |
|---|---|---|---|
| **E1: label printer firmware push** (2025-03) | A "routine" firmware push skipped the canary batch and went to every depot at once. The printers' error alerts went to an email list nobody watched, so the failure was found by depot staff hours later. | Asha Rao asked for a canary batch first. **Overruled.** Asha is still at the company. | Yes: the internal lesson "The quiet push" |
| **E2: invoice export cutover** (2025-07) | A cutover was delayed after review found a missing reconciliation step. | Mei Okafor flagged it. **Accepted.** | No (a near-incident, kept as history) |

## Current plans (what NODUS watches)
| Plan | Demo role (D12) | Shape | Expected |
|---|---|---|---|
| **Refresh tariff tables for every depot** | **hero** | routine; no canary procedure; one automated format checker; alerts go to an email list watched only by someone who left; **no final "send to all depots" step yet** | Antibody 1: 4/5 foresight · Antibody 2: 3/4 foresight · internal lesson: 4/5 foresight |
| **Swap map tile provider in the driver app** | **internal echo** | standard risk; skips canary; two gates; alerts to an unwatched email list; switch-over to all drivers scheduled | internal lesson: 5/5 full |
| **Global rollout of dock sensor content update** | **control** | *sounds* like CrowdStrike, but follows the staged procedure, has a human review, and its alerts page the on-call | no echo (all partial) |
| **Scanner handheld OS patch** | **near-miss** | routine, skips canary, but has a human gate and watched alerts | Antibody 1: 3/5 partial |
| **Billing report column rename** | **clean** | follows procedure, human review, watched pager | nothing |

**Silence** in the hero: its alert channel has **no owner** and **no active watcher**.

**Witness** for the hero: Asha Rao, who raised the overruled concern in E1, the
episode behind the internal lesson the hero echoes.

## Seeded background
A seeded generator adds background plans (all done, all followed the staged procedure),
so "most changes follow the procedure" is a fact in the graph, not an assumption.
Same seed → same world.
