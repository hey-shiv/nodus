# Post-mortem: label printer firmware push

> SYNTHETIC. Tern & Tally Freight is a fictional company invented for the NODUS demo.
> Blameless format: we describe systems and decisions, not individual fault.

**Author:** Tomas Lind · **Incident date:** 2025-03-19 · **Status:** closed

## Summary
A firmware update for the label printers reached every depot at the same time and
stopped label printing for about six hours. Parcels could not be dispatched until the
previous firmware was restored.

## Timeline (UTC)
- 08:00 The firmware push started. It went to all depots in one step.
- 08:05 Printers began rejecting jobs. Each printer sent error alerts.
- 11:40 Depot staff reported that no labels were printing.
- 14:10 The previous firmware was restored at every depot.

## Contributing factors
- The update was filed as a routine change because the vendor had shipped many similar updates before.
- Most changes at Tern & Tally go through the canary procedure: a small batch of depots first, then everyone.
- This change did not follow the canary procedure.
- The only check before release was the automated config schema lint.
- The printer error alerts went to the printer-alerts email list.
- Nobody was watching the printer-alerts email list, so the alerts went unread for more than three hours.
- The firmware was sent to every depot at once, so every depot failed together.

## Concerns raised before the change
- During planning, Asha Rao asked for a canary batch of two depots first. The request was declined to keep the release on schedule.

## Action items
- Route printer alerts to the on-call pager.
- Require the canary procedure for firmware changes, including routine ones.
- Give every alert channel a named owner.
