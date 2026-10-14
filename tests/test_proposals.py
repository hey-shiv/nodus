"""T14: lesson proposals are checked before any human sees them. No real LLM calls."""
import json
from pathlib import Path

import pytest

from nodus.llm import LLM, LLMError
from nodus.proposals import ProposalRejected, propose_lesson
from nodus.lessons import load_sources

DOC = Path("data/postmortems/e1-label-printer.md").read_text()
GOOD = Path("data/lessons/internal-quiet-push.json").read_text()


class Scripted:
    """A fake provider that returns prepared replies in order."""
    name = "fake"

    def __init__(self, *replies):
        self.replies, self.calls = list(replies), 0

    def complete(self, prompt):
        self.calls += 1
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def make_llm(tmp_path, *providers):
    return LLM(providers=list(providers), cache_dir=tmp_path)


def test_valid_draft_is_accepted(tmp_path):
    llm = make_llm(tmp_path, Scripted(GOOD))
    lesson = propose_lesson(llm, "doc-pm-e1", DOC, load_sources(), "internal-quiet-push")
    assert lesson.completion == "Q.5" and len(lesson.conditions) == 5


def test_invented_quote_is_rejected_and_quarantined(tmp_path, monkeypatch):
    import nodus.proposals as p
    monkeypatch.setattr(p, "QUARANTINE", tmp_path / "q")
    bad = json.loads(GOOD)
    bad["conditions"][1]["citations"][0]["quote"] = "The team skipped the canary to save time."
    llm = make_llm(tmp_path, Scripted(*[json.dumps(bad)] * 3))
    with pytest.raises(ProposalRejected, match="not found verbatim"):
        propose_lesson(llm, "doc-pm-e1", DOC, load_sources(), "x")
    assert (tmp_path / "q" / "x.json").exists()


def test_broken_json_is_retried(tmp_path):
    llm = make_llm(tmp_path, Scripted("{not json", GOOD))
    lesson = propose_lesson(llm, "doc-pm-e1", DOC, load_sources(), "internal-quiet-push")
    assert lesson.id == "internal-quiet-push"


def test_unknown_relationship_is_rejected(tmp_path, monkeypatch):
    import nodus.proposals as p
    monkeypatch.setattr(p, "QUARANTINE", tmp_path / "q")
    bad = json.loads(GOOD)
    bad["conditions"][0]["path"] = [["BLAMES", "out"]]
    llm = make_llm(tmp_path, Scripted(*[json.dumps(bad)] * 3))
    with pytest.raises(ProposalRejected, match="does not compile"):
        propose_lesson(llm, "doc-pm-e1", DOC, load_sources(), "x")


def test_falls_back_to_next_provider_when_first_fails(tmp_path):
    quota = Scripted(LLMError("gemini: 429 RESOURCE_EXHAUSTED"))
    local = Scripted('{"ok": true}')
    assert make_llm(tmp_path, quota, local).complete_json("hi") == '{"ok": true}'
    assert (quota.calls, local.calls) == (1, 1)


def test_reply_is_cached(tmp_path):
    fake = Scripted('{"a": 1}')
    llm = make_llm(tmp_path, fake)
    llm.complete_json("same prompt")
    llm.complete_json("same prompt")
    assert fake.calls == 1


def test_prompt_shows_the_shape_of_object_fields():
    from nodus.proposals import build_prompt
    prompt = build_prompt("doc-pm-e1", "text", "x")
    assert '"all_targets": {"kind": "automated"}' in prompt
    assert '"completion" must equal one condition' in prompt
