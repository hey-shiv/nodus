"""Severity: a published rule, not a judgement (plan B6). Pure: no database, no UI.

| k of n          | missing condition        | level      |
|-----------------|--------------------------|------------|
| n of n          | -                        | full       |
| n-1 of n        | the completion step      | foresight  |
| n-1 of n        | any other condition      | strong     |
| >= NOTE_SHARE   | -                        | note       |
| below           | -                        | ignore     |
"""

NOTE_SHARE = 0.5        # chosen on the demo world only (plan E3); half or more = a quiet note
WARNING_LEVELS = ("full", "foresight", "strong")


def level(k, n, missing, completion):
    if n <= 0:
        return "ignore"
    if k == n:
        return "full"
    if k == n - 1:
        return "foresight" if missing == [completion] else "strong"
    if k / n >= NOTE_SHARE:
        return "note"
    return "ignore"


def is_warning(lvl):
    return lvl in WARNING_LEVELS
