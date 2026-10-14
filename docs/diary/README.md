# The NODUS build diary

This folder records how NODUS was built during Graph Hacks (Oct 15 to 18, 2026),
step by step. For every step it says what was done, why, how the underlying idea
works from first principles, and every question asked along the way with its answer.

It exists for two readers:
1. **Me, the builder.** I started the event with one day of the prep curriculum done
   (I was ill), so most of this stack is new to me. Writing down the "why" is how I
   make sure I understand every line I ship.
2. **The judges.** The rules say entrants must understand and explain their code,
   graph model, queries and decisions. This diary is the evidence that I do.

## Files

| File | What it holds |
|---|---|
| `LOG.md` | The running journal: one entry per step, in order. Start here. |
| `00-brief.md` | What NODUS is, in my own words, written before any code. |
| `BLUEPRINT.md` | The stack, data, modules and build order, written by me, reviewed by Claude. |
| `NN-<slice>.md` | One milestone entry per working vertical slice, each with a run check and teach-back. |
| `GLOSSARY.md` | New terms, defined in my own words. |
| `.jots.md` | Quick scratch notes taken during the build (decisions, bugs, fixes). Cross-checked against milestone entries. |

## How a step gets logged

Each `LOG.md` entry uses the same parts:
- **What:** what was done, concretely.
- **Why:** the reason, including what goes wrong without it.
- **First principles:** how the underlying thing actually works.
- **Q&A:** every question asked during the step (by me or by Claude) and the answer.
- **Open:** anything left undecided, to come back to.

## Who wrote what

The decisions, the brief, the blueprint and the teach-back answers are mine.
Claude Code (AI) helped explain concepts, write code I approved function by function,
and draft log entries that I checked. See `AI_USE.md` at the repo root.
