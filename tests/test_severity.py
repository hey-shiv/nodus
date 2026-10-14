"""T19: one test per row of the B6 table."""
from nodus.severity import is_warning, level


def test_all_conditions_is_full():
    assert level(5, 5, [], "C5") == "full"


def test_only_completion_missing_is_foresight():
    assert level(4, 5, ["C5"], "C5") == "foresight"


def test_other_condition_missing_is_strong():
    assert level(4, 5, ["C2"], "C5") == "strong"


def test_half_or_more_is_note():
    assert level(3, 5, ["C4", "C5"], "C5") == "note"
    assert level(2, 4, ["C1", "C2"], "C4") == "note"      # exactly half counts as a note


def test_below_half_is_ignored():
    assert level(2, 5, ["C3", "C4", "C5"], "C5") == "ignore"


def test_only_top_three_levels_warn():
    assert [l for l in ("full", "foresight", "strong", "note", "ignore") if is_warning(l)] == \
        ["full", "foresight", "strong"]
