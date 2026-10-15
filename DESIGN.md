---
version: alpha
name: Blueprint Ledger
description: The NODUS interface. A plan is checked against the drawing of a past failure, so the screen is a drawing sheet. For plan owners and reviewers reading echoes, a few minutes at a time.

colors:
  primary: "#23241F"
  secondary: "#5A5B53"
  tertiary: "#B63A17"
  tertiary-line: "#DE5A2E"
  neutral: "#E5E3DA"
  surface: "#F1F0EA"
  on-surface: "#1B1C18"
  border: "#B9B7AC"
  error: "#8E2C12"

typography:
  display:
    fontFamily: Archivo
    fontSize: 56px
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Archivo
    fontSize: 34px
    fontWeight: 800
    lineHeight: 1.04
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Archivo
    fontSize: 22px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: -0.01em
  title:
    fontFamily: Archivo
    fontSize: 18px
    fontWeight: 700
    lineHeight: 1.3
  body-lg:
    fontFamily: Archivo
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.55
  body-md:
    fontFamily: Archivo
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  quote:
    fontFamily: Archivo
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0em
  label-caps:
    fontFamily: IBM Plex Mono
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: 0.08em
  spec:
    fontFamily: IBM Plex Mono
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
  data:
    fontFamily: IBM Plex Mono
    fontSize: 15px
    fontWeight: 500
    lineHeight: 1.3

rounded:
  none: 0px
  hairline: 2px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px

components:
  page:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
  sheet-title:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.display}"
  section-title:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.headline-lg}"
  ledger-row-title:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.headline-md}"
  spec-sheet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary}"
    typography: "{typography.spec}"
    padding: "{spacing.md}"
  spec-label:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary}"
    typography: "{typography.label-caps}"
  count:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.data}"
  completion-mark:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.tertiary}"
    typography: "{typography.label-caps}"
  completion-line:
    backgroundColor: "{colors.tertiary-line}"
    width: 2px
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.none}"
    padding: "{spacing.md}"
  button-primary-hover:
    backgroundColor: "{colors.on-surface}"
    textColor: "{colors.neutral}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.none}"
    padding: "{spacing.md}"
  panel:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.none}"
    padding: "{spacing.lg}"
  quote-block:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.on-surface}"
    typography: "{typography.quote}"
    padding: "{spacing.md}"
  rule:
    backgroundColor: "{colors.border}"
    height: 1px
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.hairline}"
    padding: "{spacing.sm}"
  input-error:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.error}"
    typography: "{typography.body-lg}"
---

# Blueprint Ledger

## Overview

NODUS checks a plan against the drawing of a past failure, condition by condition, so the
interface is a **drawing sheet**: warm paper, graphite linework, square corners, a technical spec
table, and one red mark. The reference is Heron AI's architectural presentation (hairline building
elevations on off-white stock, an uppercase grotesk headline, a monospace "TYPE : …" spec block, and
a single vermilion marker), carried over because NODUS also reads structure the way an architect
reads a section: what is connected, what is load-bearing, what is missing.

The register is **calm, exact, slightly austere**. A reviewer should feel they are reading an
engineering document, not a dashboard trying to alarm them. Urgency comes from one thing only: the
vermilion completion mark.

**What this direction gives up:** colour as decoration and colour as status. There is no green
"success", no blue link colour, no coloured call-to-action, no dark mode, no rounded softness. In
exchange the one red mark is unmissable, and every state is legible in greyscale print.

## Colors

The palette is drawing-office materials: paper, graphite, a pencil grey, and the orange-red of a
reviewer's correction pencil.

- **Paper (surface):** warm, faintly green-grey drawing stock. Never pure white: white reads as an
  empty app, paper reads as a document someone drew.
- **Graphite (primary) and deep graphite (on-surface):** all linework, text, conditions that hold,
  and every interactive control. A condition that *holds* is drawn in graphite, not green, because
  a condition holding is not good news.
- **Pencil (secondary):** spec labels, captions, sources. Passes AA on paper; never used for anything
  the reader must act on.
- **Tracing (neutral):** panels and quote blocks, one tonal step down from paper instead of a shadow.
- **Hairline (border):** decorative rules and frames only (they carry no information, so they may
  sit below 3:1). Marks that carry meaning, such as an empty condition square, are drawn in pencil.
- **Vermilion (tertiary, tertiary-line):** the reviewer's red pencil. It has exactly **one job: the
  completion step**, the step not to take. The darker ink is for text; the brighter line value is for
  drawn strokes: a non-text graphic, so it needs 3:1 against paper (it has 3.3:1), not the 4.5:1
  for text. It covers far less than 5% of any screen.
- **Oxide (error):** a darker, browner member of the vermilion family for form errors, so an error
  never looks like a completion mark.

## Typography

**Archivo** (SIL Open Font License) does the talking: 800 weight, uppercase, tight negative
tracking for sheet titles, the way Heron sets its headline; regular 400 for body text. **IBM Plex
Mono** (OFL) does the labelling: spec-sheet labels, counts like "4 OF 5", condition ids, sources.
Mono is used here because the screen is a technical document and its labels are data, the way a
drawing's title block is lettered, not as decoration. Fallbacks: `Archivo, "Helvetica Neue", Arial,
sans-serif` and `"IBM Plex Mono", ui-monospace, Menlo, monospace`. Weights are 400 and 700/800
only, far apart on purpose. Uppercase is reserved for sheet titles, section titles, and mono labels;
body text and plan names stay in sentence case, so real names never shout.

## Layout

Flush-left on a single sheet, max 1080px, framed by a hairline border with **registration crosses**
at the corners, like a plotted drawing. An 8px base; sections separate with 32–64px and a full-width
hairline, never with cards. Body text measure stays under 72 characters. Ledgers (plans, lessons,
inbox) are rows divided by hairlines, with the row's facts in a two-column mono spec block. On narrow
screens the spec block stacks label above value, and the alignment drawing scales to the width.

## Elevation & Depth

Flat. There are **no shadows anywhere**. Hierarchy comes from (1) type weight and size, (2) hairline
rules and frames, (3) one tonal step (tracing) for panels and quotes. Focus is shown with a 2px
graphite outline offset by 2px, never a glow.

## Shapes

Square. Zero radius on buttons, panels, frames and markers; a 2px radius only on text inputs so the
browser's caret area doesn't look clipped. Markers in the shape strip and the alignment drawing are
**squares** (Heron's red square markers): a filled graphite square for a condition that holds, an
outlined square with a slash for a silence (∅), a dashed vermilion square for the missing completion
step, a light outline for a condition not present. Lines follow the same code: solid graphite (holds),
dashed graphite (∅), long-dash vermilion (completion), faint dotted (not present).

## Components

- **Sheet title:** one per page, uppercase Archivo 800, states the finding in plain words ("ONE STEP
  FROM 'THE TRUSTED CHANGE, EVERYWHERE AT ONCE'").
- **Spec sheet:** two columns, mono label (pencil, uppercase) and value (graphite), separated by " : ",
  e.g. LESSON : …, MATCH : 4 OF 5, COMPLETION : …, WITNESS : …. Used on the Echo page and in ledger rows.
- **Shape strip:** one square per condition in condition order; the completion step is always the
  last square. It has a text equivalent ("4 of 5") next to it.
- **Alignment drawing:** the past failure (left) and the plan (right), joined by condition lines with
  the marker code above; a dimension-line header reading "4 OF 5". Drawn only from the match result.
- **Buttons:** primary is solid graphite with paper text and an arrow cell divided by a hairline,
  like Heron's "LEARN MORE | →"; secondary is paper with a graphite hairline. Never vermilion.
- **Quote block:** tracing panel with a graphite left rule, the quote in regular Archivo, the source
  in mono below.

## Do's and Don'ts

- Do use vermilion **only** for the completion step and its label. If something else needs emphasis,
  use weight, size or space.
- Don't colour-code conditions with green, amber or red; state is shape and line style first, with
  "k of n" in text beside it.
- Do keep every corner square, except the 2px input radius.
- Don't add shadows, gradients, glassmorphism or emoji; depth is hairlines and one tonal step.
- Do set titles and labels in uppercase and everything a person wrote (plan names, quotes, reasons) in
  sentence case.
- Don't put mono on body text; mono is for labels, counts, ids and sources.
- Do pair every icon-like marker with text (the ∅ marker sits beside "not recorded in the company graph").
- Don't animate anything on load; the only motion is Streamlit's own state changes. Audio never autoplays.
