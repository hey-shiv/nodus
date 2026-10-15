"""The alignment drawing: the past failure's shape (left) beside the plan (right).

A pure function of display rows (nodus.view.rows_for), which come only from the match result.
Drawn as a technical sheet (DESIGN.md "Blueprint Ledger"): graphite linework on paper, square
markers, a dimension line for "k OF n", registration crosses, and vermilion ONLY for the
completion step. State is carried by shape and line style, never by colour alone:
  holds        solid graphite line, filled square
  silence (∅)  dashed graphite line, outlined square with a slash
  completion   long-dash vermilion line, dashed vermilion square with "?"
  not present  faint dotted line, empty outlined square
"""
from html import escape
from textwrap import wrap

from nodus.theme import COLORS, DISPLAY, MONO

INK, PENCIL, PAPER, RULE = COLORS["primary"], COLORS["secondary"], COLORS["surface"], COLORS["border"]
RED, RED_INK = COLORS["tertiary-line"], COLORS["tertiary"]
WIDTH, TOP, ROW_H = 840, 132, 86
LEFT_X, COL_W = 64, 290
RIGHT_X = WIDTH - 24 - COL_W
MID_X = (LEFT_X + COL_W + RIGHT_X) // 2


def _lines(text, width=34, max_lines=2):
    out = wrap(text, width) or [""]
    if len(out) > max_lines:
        out = out[:max_lines]
        out[-1] = out[-1][: width - 1] + "…"
    return out


def _text(x, y, text, size=15, weight=400, fill=INK, anchor="start", font=DISPLAY, spacing=0,
          width=34):
    tspans = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else size + 4}">{escape(line)}</tspan>'
                     for i, line in enumerate(_lines(text, width)))
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{spacing}" fill="{fill}" text-anchor="{anchor}">{tspans}</text>')


def _cross(x, y, size=7):
    return (f'<path d="M{x - size} {y}H{x + size}M{x} {y - size}V{y + size}" stroke="{INK}" '
            f'stroke-width="1"/>')


def _marker(row, x, y, s=9):
    box = f'x="{x - s}" y="{y - s}" width="{2 * s}" height="{2 * s}"'
    if row.completion and row.state != "holds":
        return (f'<rect {box} fill="{PAPER}" stroke="{RED}" stroke-width="2" stroke-dasharray="4 3"/>'
                f'<text x="{x}" y="{y + 4.5}" font-family="{MONO}" font-size="12" font-weight="600" '
                f'fill="{RED_INK}" text-anchor="middle">?</text>')
    if row.state == "holds" and row.absence:
        return (f'<rect {box} fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
                f'<path d="M{x - s + 3} {y + s - 3}L{x + s - 3} {y - s + 3}" stroke="{INK}" '
                f'stroke-width="1.5"/>')
    if row.state == "holds":
        return f'<rect {box} fill="{INK}"/>'
    return f'<rect {box} fill="{PAPER}" stroke="{PENCIL}" stroke-width="1"/>'


def _connector(row, y):
    x1, x2 = LEFT_X + COL_W + 10, RIGHT_X - 10
    if row.completion and row.state != "holds":
        return (f'<line class="completion" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
                f'stroke="{RED}" stroke-width="2" stroke-dasharray="10 6"/>')
    if row.state == "holds" and row.absence:
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{INK}" stroke-width="1.5" '
                f'stroke-dasharray="5 4"/>')
    if row.state == "holds":
        return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{INK}" stroke-width="1.5"/>'
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{PENCIL}" stroke-width="1" '
            f'stroke-dasharray="1 5"/>')


def _dimension(y, k, n):
    """An architect's dimension line across the gap, reading 'k OF n'."""
    x1, x2 = LEFT_X + COL_W + 10, RIGHT_X - 10
    return (f'<path d="M{x1} {y - 6}V{y + 6}M{x2} {y - 6}V{y + 6}M{x1} {y}H{MID_X - 34}'
            f'M{MID_X + 34} {y}H{x2}" stroke="{INK}" stroke-width="1"/>'
            f'<text class="count" x="{MID_X}" y="{y + 5}" font-family="{MONO}" font-size="15" '
            f'font-weight="600" fill="{INK}" text-anchor="middle">{k} OF {n}</text>')


def alignment_svg(lesson_name, plan_title, rows, k, n, level):
    height = TOP + ROW_H * len(rows) + 36
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="100%" role="img" aria-labelledby="t d" style="max-width:{WIDTH}px">',
        f'<title id="t">{escape(lesson_name)} beside {escape(plan_title)}: {k} of {n}</title>',
        f'<desc id="d">Each row pairs one condition of the past failure with what the plan '
        f'contains. {k} of {n} conditions hold; level: {escape(level)}.</desc>',
        f'<rect width="{WIDTH}" height="{height}" fill="{PAPER}"/>',
        f'<rect x="8.5" y="8.5" width="{WIDTH - 17}" height="{height - 17}" fill="none" '
        f'stroke="{RULE}"/>',
        _cross(8.5, 8.5), _cross(WIDTH - 8.5, 8.5), _cross(8.5, height - 8.5),
        _cross(WIDTH - 8.5, height - 8.5),
        _text(LEFT_X, 38, "THE PAST FAILURE", 11, 500, PENCIL, font=MONO, spacing=1.2),
        _text(LEFT_X, 62, lesson_name, 17, 800, INK, width=30),
        _text(RIGHT_X, 38, "THIS PLAN", 11, 500, PENCIL, font=MONO, spacing=1.2),
        _text(RIGHT_X, 62, plan_title, 17, 800, INK, width=30),
        _dimension(62, k, n),
        f'<line x1="{LEFT_X}" y1="{TOP - 18}" x2="{WIDTH - 24}" y2="{TOP - 18}" stroke="{INK}" '
        f'stroke-width="1"/>',
    ]
    for i, row in enumerate(rows):
        y = TOP + i * ROW_H + 18
        red = row.completion and row.state != "holds"
        parts.append(f'<g class="row {escape(row.state)}"><title>{escape(row.cid)}: '
                     f'{escape(row.lesson_text)} | plan: {escape(row.plan_text)}</title>')
        parts.append(_text(24, y, row.cid, 11, 500, RED_INK if red else PENCIL, font=MONO))
        parts.append(_text(LEFT_X, y, row.lesson_text, 15, 700 if red else 400,
                           RED_INK if red else INK))
        parts.append(_text(LEFT_X, y + 42, row.source.upper(), 10, 500, PENCIL, font=MONO,
                           spacing=0.8, width=46))
        parts.append(_connector(row, y + 6))
        parts.append(_marker(row, MID_X, y + 6))
        colour = RED_INK if red else (INK if row.state == "holds" else PENCIL)
        parts.append(_text(RIGHT_X, y, row.plan_text, 15, 400, colour))
        if red:
            parts.append(_text(RIGHT_X, y + 42, "THE STEP THAT WOULD COMPLETE IT", 10, 600,
                               RED_INK, font=MONO, spacing=0.8, width=46))
        elif row.state == "holds" and row.absence:
            parts.append(_text(RIGHT_X, y + 42, "NOT RECORDED IN THE COMPANY GRAPH", 10, 500,
                               PENCIL, font=MONO, spacing=0.8, width=46))
        parts.append(f'<line x1="{LEFT_X}" y1="{y + ROW_H - 26}" x2="{WIDTH - 24}" '
                     f'y2="{y + ROW_H - 26}" stroke="{RULE}" stroke-width="0.75"/>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def shape_strip(states, completion_index, size=13, gap=5):
    """The k-of-n strip used in lists: one square per condition, completion last."""
    order = [i for i in range(len(states)) if i != completion_index] + [completion_index]
    w = len(states) * (size + gap)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{size + 2}" '
           f'viewBox="0 0 {w} {size + 2}" aria-hidden="true">']
    for slot, i in enumerate(order):
        holds, absence = states[i]
        x, y = slot * (size + gap) + 1, 1
        box = f'x="{x}" y="{y}" width="{size}" height="{size}"'
        if i == completion_index and not holds:
            out.append(f'<rect {box} fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="3 2"/>')
        elif holds and absence:
            out.append(f'<rect {box} fill="none" stroke="{INK}" stroke-width="1.5"/>'
                       f'<path d="M{x + 2} {y + size - 2}L{x + size - 2} {y + 2}" stroke="{INK}" '
                       f'stroke-width="1.5"/>')
        elif holds:
            out.append(f'<rect {box} fill="{INK}"/>')
        else:
            out.append(f'<rect {box} fill="none" stroke="{PENCIL}" stroke-width="1"/>')
    out.append("</svg>")
    return "".join(out)
