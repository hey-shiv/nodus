"""The alignment picture: the past failure's shape (left) beside the plan (right).

A pure function of display rows (nodus.view.rows_for), which come only from the match
result. Nothing here is hand-drawn: change the graph and the picture changes.
"""
from html import escape
from textwrap import wrap

INK, PAPER, RULE = "#1E2B2F", "#F2F4F0", "#CBD3D0"
HOLDS, COMPLETION, SILENCE, MUTED = "#2E7A68", "#B42318", "#6E64A0", "#8A9693"
WIDTH, TOP, ROW_H = 820, 116, 84
LEFT_X, COL_W = 20, 300
RIGHT_X = WIDTH - 24 - COL_W
MID_X = WIDTH // 2
FONT = "Atkinson Hyperlegible, system-ui, sans-serif"


def _lines(text, width=36, max_lines=2):
    out = wrap(text, width) or [""]
    if len(out) > max_lines:
        out = out[:max_lines]
        out[-1] = out[-1][: width - 1] + "…"
    return out


def _text(x, y, text, size=15, weight=400, fill=INK, anchor="start"):
    tspans = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else size + 4}">{escape(line)}</tspan>'
                     for i, line in enumerate(_lines(text)))
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{tspans}</text>')


def _marker(row, x, y):
    if row.completion and row.state != "holds":
        return (f'<circle cx="{x}" cy="{y}" r="11" fill="{PAPER}" stroke="{COMPLETION}" '
                f'stroke-width="2.5" stroke-dasharray="4 3"/>'
                f'<text x="{x}" y="{y + 5}" font-family="{FONT}" font-size="14" font-weight="700" '
                f'fill="{COMPLETION}" text-anchor="middle">?</text>')
    if row.state == "holds" and row.absence:
        return (f'<circle cx="{x}" cy="{y}" r="11" fill="{SILENCE}"/>'
                f'<text x="{x}" y="{y + 5}" font-family="{FONT}" font-size="14" font-weight="700" '
                f'fill="{PAPER}" text-anchor="middle">∅</text>')
    if row.state == "holds":
        return (f'<circle cx="{x}" cy="{y}" r="11" fill="{HOLDS}"/>'
                f'<text x="{x}" y="{y + 5}" font-family="{FONT}" font-size="14" font-weight="700" '
                f'fill="{PAPER}" text-anchor="middle">✓</text>')
    return (f'<circle cx="{x}" cy="{y}" r="11" fill="{PAPER}" stroke="{MUTED}" stroke-width="2"/>'
            f'<text x="{x}" y="{y + 5}" font-family="{FONT}" font-size="13" fill="{MUTED}" '
            f'text-anchor="middle">–</text>')


def _connector(row, y):
    x1, x2 = LEFT_X + COL_W + 8, RIGHT_X - 8
    if row.completion and row.state != "holds":
        return (f'<line class="completion" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
                f'stroke="{COMPLETION}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    if row.state == "holds":
        colour = SILENCE if row.absence else HOLDS
        return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{colour}" stroke-width="2.5"/>'
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{RULE}" stroke-width="1.5" '
            f'stroke-dasharray="2 5"/>')


def alignment_svg(lesson_name, plan_title, rows, k, n, level):
    height = TOP + ROW_H * len(rows) + 28
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="100%" role="img" aria-labelledby="t d" style="max-width:{WIDTH}px">',
        f'<title id="t">{escape(lesson_name)} beside {escape(plan_title)}: {k} of {n}</title>',
        f'<desc id="d">Each row pairs one condition of the past failure with what the plan '
        f'contains. {k} of {n} conditions hold; level: {escape(level)}.</desc>',
        f'<rect width="{WIDTH}" height="{height}" fill="{PAPER}"/>',
        _text(LEFT_X, 30, "The past failure", 13, 700, MUTED),
        _text(LEFT_X, 54, lesson_name, 18, 700),
        _text(RIGHT_X, 30, "This plan", 13, 700, MUTED),
        _text(RIGHT_X, 54, plan_title, 18, 700),
        f'<text class="count" x="{MID_X}" y="54" font-family="{FONT}" font-size="22" '
        f'font-weight="700" fill="{INK}" text-anchor="middle">{k} of {n}</text>',
        f'<line x1="{LEFT_X}" y1="{TOP - 14}" x2="{WIDTH - 24}" y2="{TOP - 14}" stroke="{RULE}"/>',
    ]
    for i, row in enumerate(rows):
        y = TOP + i * ROW_H + 24
        parts.append(f'<g class="row {escape(row.state)}"><title>{escape(row.cid)}: '
                     f'{escape(row.lesson_text)} | plan: {escape(row.plan_text)}</title>')
        parts.append(_text(LEFT_X, y, row.lesson_text, 15, 700 if row.completion else 400,
                           COMPLETION if row.completion and row.state != "holds" else INK))
        parts.append(_text(LEFT_X, y + 40, row.source, 12, 400, MUTED))
        parts.append(_connector(row, y + 6))
        parts.append(_marker(row, MID_X, y + 6))
        colour = (SILENCE if row.absence and row.state == "holds" else
                  COMPLETION if row.completion and row.state != "holds" else
                  INK if row.state == "holds" else MUTED)
        parts.append(_text(RIGHT_X, y, row.plan_text, 15, 400, colour))
        if row.completion and row.state != "holds":
            parts.append(_text(RIGHT_X, y + 40, "the step that would complete it", 12, 700,
                               COMPLETION))
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def shape_strip(states, completion_index, size=14, gap=6):
    """The small k-of-n strip used in lists: one tick per condition."""
    w = len(states) * (size + gap)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{size + 4}" '
           f'viewBox="0 0 {w} {size + 4}" aria-hidden="true">']
    for i, (holds, absence) in enumerate(states):
        x, cy, r = i * (size + gap) + size / 2 + 1, size / 2 + 2, size / 2
        if i == completion_index and not holds:
            out.append(f'<circle cx="{x}" cy="{cy}" r="{r - 1.5}" fill="none" stroke="{COMPLETION}" '
                       f'stroke-width="2" stroke-dasharray="3 2"/>')
        elif holds:
            out.append(f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{SILENCE if absence else HOLDS}"/>')
        else:
            out.append(f'<circle cx="{x}" cy="{cy}" r="{r - 1.5}" fill="none" stroke="{RULE}" '
                       f'stroke-width="2"/>')
    out.append("</svg>")
    return "".join(out)
