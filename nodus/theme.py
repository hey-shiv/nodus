"""Design tokens from DESIGN.md ("Blueprint Ledger"). One place for colours and faces.

tests/test_theme.py checks these against DESIGN.md's frontmatter so they can't drift.
"""
COLORS = {
    "primary": "#23241F",        # graphite: linework, text, conditions that hold, controls
    "secondary": "#5A5B53",      # pencil: labels, captions, sources, empty marks
    "tertiary": "#B63A17",       # vermilion ink: the completion step, as text
    "tertiary-line": "#DE5A2E",  # vermilion stroke: the completion step, as a line (non-text, 3:1)
    "neutral": "#E5E3DA",        # tracing: panels and quote blocks
    "surface": "#F1F0EA",        # paper
    "on-surface": "#1B1C18",     # deep graphite: body text
    "border": "#B9B7AC",         # hairline: decorative rules and frames only
    "error": "#8E2C12",          # oxide: form errors, never a completion mark
}
DISPLAY = "Archivo, 'Helvetica Neue', Arial, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, Menlo, monospace"
