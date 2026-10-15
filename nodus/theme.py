"""Design tokens from DESIGN.md ("Paper and Post"). One place for colours and faces.

tests/test_theme.py checks these against DESIGN.md's frontmatter so they can't drift.
"""
COLORS = {
    "primary": "#232323",        # ink: text, conditions that hold, the main button's text colour on white
    "secondary": "#5F5E57",      # muted: supporting text, sources, empty marks
    "tertiary": "#9A3F1F",       # terracotta ink: the completion step, as text
    "tertiary-line": "#C2643F",  # terracotta stroke: the completion step, as a line (non-text, 3:1)
    "neutral": "#FCF8EF",        # paper, one step deeper: quotes and inset panels
    "surface": "#FFFFFF",        # white cards (Sarvam)
    "on-surface": "#232323",     # text on cards
    "border": "#E6E1D4",         # card borders and rules
    "error": "#8A2B12",          # form errors
    "paper": "#FFFBF2",          # page background (Bharat Digital)
    "peri": "#B6C4FD",           # periwinkle: clouds, bullets
    "peri-soft": "#DCE4FF",      # periwinkle wash: pill labels, active tab
    "peri-ink": "#212191",       # periwinkle ink: text on the wash
    "sage": "#B9C69E",           # sage: the drawers
    "olive": "#606C47",          # olive: small mono labels
    "navy": "#2A2C33",           # the primary button (Sarvam)
}
SANS = "'Public Sans', Helvetica, Arial, sans-serif"
SERIF = "'Libertinus Serif', Georgia, serif"
MONO = "'DM Mono', ui-monospace, Menlo, monospace"
DISPLAY = SANS   # kept for older imports
