---
version: alpha
name: Paper and Post
description: The NODUS website. A calm, plain-language page about remembering past failures, for anyone (judges, managers, engineers) seeing NODUS for the first time.

colors:
  primary: "#232323"
  secondary: "#5F5E57"
  tertiary: "#9A3F1F"
  tertiary-line: "#C2643F"
  neutral: "#FCF8EF"
  surface: "#FFFFFF"
  on-surface: "#232323"
  border: "#E6E1D4"
  error: "#8A2B12"
  paper: "#FFFBF2"
  peri: "#B6C4FD"
  peri-soft: "#DCE4FF"
  peri-ink: "#212191"
  sage: "#B9C69E"
  olive: "#606C47"
  navy: "#2A2C33"

typography:
  display:
    fontFamily: Libertinus Serif Display
    fontSize: 64px
    fontWeight: 400
    lineHeight: 1.12
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Libertinus Serif
    fontSize: 44px
    fontWeight: 400
    lineHeight: 1.18
    letterSpacing: -0.2px
  headline-md:
    fontFamily: Libertinus Serif
    fontSize: 27px
    fontWeight: 400
    lineHeight: 1.22
  opener:
    fontFamily: Libertinus Serif
    fontSize: 26px
    fontWeight: 400
    lineHeight: 1.3
  body-lg:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  button:
    fontFamily: Public Sans
    fontSize: 15px
    fontWeight: 500
    lineHeight: 1.2
  label-caps:
    fontFamily: DM Mono
    fontSize: 12.5px
    fontWeight: 500
    lineHeight: 1.6
    letterSpacing: 1.75px
  logo:
    fontFamily: League Spartan
    fontSize: 25px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: -0.02em

rounded:
  none: 0px
  sm: 12px
  md: 18px
  full: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 112px

components:
  page:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
  hero-title:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.primary}"
    typography: "{typography.display}"
  section-opener:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.secondary}"
    typography: "{typography.opener}"
  section-title:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.primary}"
    typography: "{typography.headline-lg}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
  card-title:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.headline-md}"
  quote:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    padding: "{spacing.md}"
  label:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.olive}"
    typography: "{typography.label-caps}"
  logo:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.primary}"
    typography: "{typography.logo}"
  button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.surface}"
    typography: "{typography.button}"
    rounded: "{rounded.full}"
    padding: "{spacing.md}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.button}"
    rounded: "{rounded.full}"
    padding: "{spacing.md}"
  pill-label:
    backgroundColor: "{colors.peri-soft}"
    textColor: "{colors.peri-ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
  bullet:
    backgroundColor: "{colors.peri}"
    size: 8px
  drawer:
    backgroundColor: "{colors.sage}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
  completion-tag:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.tertiary}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.full}"
  completion-line:
    backgroundColor: "{colors.tertiary-line}"
    width: 2px
  rule:
    backgroundColor: "{colors.border}"
    height: 1px
  intro:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.secondary}"
    typography: "{typography.body-lg}"
  input-error:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.error}"
    typography: "{typography.body-md}"
---

# Paper and Post

## Overview

NODUS asks people to slow down before a risky step, so the site is calm and readable rather than
technical. It is a deliberate **mixture of two references, and nothing beyond them**:
[Bharat Digital](https://bharatdigital.org/) gives the paper, the serif voice, the dithered
illustration, the postage stamps and the cabinet drawers; [Sarvam](https://www.sarvam.ai/) gives the
calm centred layouts, pill labels and pill buttons, and clean white cards with soft borders.

The register is a thoughtful public-interest publication: warm, plain-spoken, a little crafted.
Everything is explained from first principles; technical detail lives on its own page.

**What it gives up:** density, dark mode, and any "dashboard" look. There are no data-heavy grids
on the home page and no jargon above the fold.

## Colors

- **Paper** is Bharat Digital's warm off-white page; **white** cards sit on it, as on Sarvam.
- **Ink** is near-black for all text and for facts that hold. A fact holding is not good news, so it
  is never green.
- **Terracotta** (tertiary and its line value) has one job: the step that would complete a
  failure. It appears as text, a dashed ring, or a soft tag, and nowhere else.
- **Periwinkle** comes from both references (Bharat's clouds, Sarvam's glow): bullets, pill labels,
  the active tab, and invitations to a person.
- **Sage** is only for the drawers; **olive** only for small mono labels; **navy** only for the one
  primary button per view.

## Typography

**Libertinus Serif Display / Libertinus Serif** (OFL) carry every headline, often mixing UPPERCASE
words with *italic* lowercase, the way Bharat Digital sets "WE *reimagine* technology". **Public Sans**
(OFL) is the body and the buttons. **DM Mono** (OFL) is only for small uppercase labels. **League
Spartan** (OFL) is only for the "nodus" wordmark. Headlines use weight 400; emphasis comes from italics,
not weight.

## Layout

A single centred column up to 1180px. The home page follows Bharat Digital's sequence: a full-width
illustration with the headline framed inside it, a short intro and two buttons, the stamp arc, then
sections each opened by a quiet "…through *something*" line. Cards and two-column text/visual
sections follow Sarvam. Generous spacing (about 112px between sections). Body text stays under 62ch.

## Elevation & Depth

Flat. Cards are white with a 1px warm border and no shadow; quotes sit on a slightly deeper paper.
The only depth effect is Sarvam's soft periwinkle and orange glow, used once, behind the final call to
action.

## Shapes

Soft but not bubbly: 18px cards, 12px quotes and inputs, fully round pills for buttons and labels.
Bharat Digital's crafted objects keep their own geometry: perforated stamps and square-cornered drawers
with a round knob. Markers are round: a filled ink dot with a tick (holds), an outlined dot with a slash
(not recorded), a dashed terracotta ring (the step not to take), an empty ring (not present).

## Components

- **Hero:** the dithered gateway illustration (generated, original), headline in its opening.
- **Stamps:** five real past failures, each with company, year, one plain sentence and a line icon.
- **Drawers:** the five things NODUS does, one per drawer, with a mono tag and a knob.
- **Checklist card:** a plan's facts with round markers, then a terracotta "4 of 5" bar.
- **Message card:** the heads-up as the owner sees it, with "not recorded" lines and the person invited.
- **Buttons:** navy primary, white secondary, both pills; one primary per view.

## Do's and Don'ts

- Do explain in plain words first; put engines, queries and protocols on "Under the hood".
- Do mix UPPERCASE and *italic* in headlines; don't bold them.
- Don't use terracotta for anything except the step that would complete a failure.
- Don't add colours, shadows or gradients beyond the single Sarvam glow.
- Don't use DM Mono for sentences; it's for short labels only.
- Do pair every marker with words ("4 of 5 already true", "not recorded").
- Don't borrow either reference's images or logos; illustrations are generated for NODUS.
