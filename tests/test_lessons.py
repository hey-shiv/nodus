"""T14-T16: lesson files validate, compile and cite; storage keeps versions."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from nodus.lessons import (Lesson, active_lessons, approve, check_compiles, load_lesson_file,
                           load_sources, store, unverified_quotes)

FILES = sorted(Path("data/lessons").glob("*.json"))
SOURCE_CACHE = Path("cache/sources")


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_lesson_file_validates_and_compiles(path):
    lesson = load_lesson_file(path)
    check_compiles(lesson)
    assert 3 <= len(lesson.conditions) <= 6


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_every_quote_is_verbatim(path):
    lesson = load_lesson_file(path)
    if lesson.origin == "public" and not SOURCE_CACHE.exists():
        pytest.skip("public source texts not cached; run scripts/verify_sources.py")
    assert unverified_quotes(lesson, load_sources()) == []


def test_lesson_without_absence_is_refused():
    data = load_lesson_file(FILES[0]).model_dump()
    for c in data["conditions"]:
        if c["kind"] == "absent":
            c["kind"] = "present"
    with pytest.raises(ValidationError, match="absence"):
        Lesson.model_validate(data)


def test_role_used_before_bound_is_refused():
    data = load_lesson_file(Path("data/lessons/antibody-2.json")).model_dump()
    data["conditions"].insert(0, data["conditions"].pop(1))   # A2.2 (uses ch) first
    with pytest.raises(ValidationError, match="before they are bound"):
        Lesson.model_validate(data)


def test_only_approved_lessons_are_active_and_edits_bump_version(graph):
    sources = load_sources()
    lesson = load_lesson_file(Path("data/lessons/antibody-1.json"))
    assert store(graph, lesson, sources) == 1
    assert active_lessons(graph) == []
    approve(graph, lesson.id, "tester")
    active = active_lessons(graph)
    assert [l["id"] for l in active] == ["antibody-1"]
    assert active[0]["conditions"][1]["bind"] == "proc"
    assert store(graph, lesson, sources) == 1                     # unchanged: same version
    edited = lesson.model_copy(update={"summary": lesson.summary + " Edited."})
    assert store(graph, edited, sources) == 2                     # edit: new version...
    assert active_lessons(graph) == []                            # ...needs approval again
