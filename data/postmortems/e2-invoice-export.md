# Review: invoice export cutover

> SYNTHETIC. Tern & Tally Freight is a fictional company invented for the NODUS demo.

**Author:** Diego Marín · **Date:** 2025-07-02 · **Status:** closed (no incident)

## Summary
The cutover to the new invoice export was delayed by five days after a review found a
missing reconciliation step. No customer impact.

## What happened
- The cutover plan followed the canary procedure and had a peer review sign-off.
- During review, Mei Okafor pointed out that totals were not reconciled between the old and new exports.
- The concern was accepted. A reconciliation step was added before the full cutover.

## Action items
- Add reconciliation to the data migration checklist.
