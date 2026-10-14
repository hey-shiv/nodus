# Data policy and sources

NODUS uses only data the rules allow: public, synthetic, or my own.

## Synthetic
- **Tern & Tally Freight** (`nodus/world.py`, `docs/world-story.md`): a fictional company,
  its people, systems, plans and incidents, generated during the event by a seeded script.
  Every node carries `origin: synthetic`. Any resemblance to real people or companies is unintended.
- **Internal post-mortems** (`data/postmortems/`): fictional, written for the demo.
- **Evaluation families** (`eval/generate.py`): synthetic, seeded, in separate graphs.

## Public (cited, quoted verbatim, not redistributed)
| Source | Used for |
|---|---|
| [Cloudflare: Details of the Cloudflare outage on July 2, 2019](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/) | Antibodies 1 and 3 |
| [CrowdStrike: Falcon Content Update Remediation and Guidance Hub (Preliminary PIR)](https://www.crowdstrike.com/falcon-content-update-remediation-and-guidance-hub/) | Antibody 1 |
| [U.S. SEC press release 2013-222 on Knight Capital](https://www.sec.gov/news/press-release/2013-222) | Antibody 2 |
| [GitLab: Postmortem of database outage of January 31](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/) | Antibody 2 |
| [AWS: Summary of the Amazon S3 Service Disruption (US-EAST-1)](https://aws.amazon.com/message/41926/) | Antibody 3 |

Each lesson condition quotes one or more exact sentences (26 quotes in total), checked
against the published pages with `scripts/verify_sources.py` on Oct 15, 2026. The page texts
are cached locally for that check and are **gitignored**: NODUS cites these documents, it
doesn't republish them. Wording is neutral: lessons describe a shape, not blame.

## Never
Private, login-protected, paywalled or personal data. No real person is named outside the
public sources' own published text.
