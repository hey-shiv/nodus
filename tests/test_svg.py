"""T26: the picture is drawn only from the match result."""
import re

import pytest

from nodus.lessons import active_lessons
from nodus.matcher import evaluate
from nodus.svg import alignment_svg, shape_strip
from nodus.view import Row, rows_for
from scripts.setup_demo import build

ROWS = [Row("C1", "A change is routine", "Org", "plan: routine", "holds", False, False),
        Row("C2", "Nobody watches <alerts>", "Org", "none recorded", "holds", True, False),
        Row("C3", "Goes everywhere at once", "Org", "not in the plan yet", "missing", False, True)]


def test_completion_step_line_is_dashed_red():
    svg = alignment_svg("Lesson", "Plan", ROWS, 2, 3, "foresight")
    line = re.search(r'<line class="completion"[^>]*>', svg).group(0)
    assert 'stroke-dasharray' in line and "#B42318" in line


def test_displayed_count_equals_k_of_n():
    svg = alignment_svg("Lesson", "Plan", ROWS, 2, 3, "foresight")
    assert re.search(r'class="count"[^>]*>2 of 3<', svg)


def test_text_is_escaped_and_accessible():
    svg = alignment_svg("Lesson", "Plan", ROWS, 2, 3, "foresight")
    assert "<alerts>" not in svg and "&lt;alerts&gt;" in svg
    assert "<title" in svg and "<desc" in svg


def test_absence_is_marked_with_empty_set():
    assert "∅" in alignment_svg("L", "P", ROWS, 2, 3, "foresight")


def test_strip_has_one_mark_per_condition():
    assert shape_strip([(True, False), (True, True), (False, False)], 2).count("<circle") == 3


@pytest.fixture
def world(graph):
    build(graph, approve_as="tester")
    return graph


def test_hero_rows_come_from_the_graph(world):
    lesson = next(l for l in active_lessons(world) if l["id"] == "antibody-1")
    rows = rows_for(world, "plan-hero", lesson, evaluate(world, "plan-hero", lesson))
    assert [r.state for r in rows] == ["holds"] * 4 + ["missing"]
    assert rows[-1].completion and rows[-1].plan_text == "not in the plan yet"
    assert "Tariff sheet format checker (automated)" in rows[3].plan_text
    assert rows[0].plan_text == "risk class: routine"
    assert rows[2].plan_text.startswith("not following")
    assert rows[0].source == "Cloudflare, CrowdStrike"
