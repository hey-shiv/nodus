"""Ask the LLM to draft a lesson from a post-mortem, then check its homework.

A draft is accepted only if it validates (shape), compiles (whitelisted names) and
every quote is found verbatim in the post-mortem. Otherwise it is retried with the
problems listed, and finally quarantined. Accepted drafts are still only *proposed*:
a human approves them (nodus.lessons.approve).
"""
import json
from pathlib import Path

from pydantic import ValidationError

from nodus.compiler import CompileError
from nodus.lessons import Lesson, check_compiles, unverified_quotes
from nodus.schema import ENDS, KIND_BY_LABEL, LABELS, PROPERTIES, RELATIONSHIPS, VOCAB

QUARANTINE = Path(__file__).resolve().parent.parent / "cache" / "quarantine"


class ProposalRejected(ValueError):
    pass


def build_prompt(doc_id, doc_text, lesson_id):
    return f"""You draft a reusable lesson from an incident post-mortem, as JSON only.

A lesson is 3 to 6 conditions describing the SHAPE of the failure with roles and
relationships, not names or blame. Each condition has one kind:
- "present": a path from a start node to a target exists. Fields: start, path, target, optional bind.
- "absent": no such path exists (something missing). Same fields.
- "attribute_equals": a property of the start node equals a value. Fields: start, property, value.
- "count_equals": exactly n paths exist, optionally all targets match. Fields: start, path, target, n, all_targets.
start is "anchor" (the plan being checked), "role:<name>" (bound earlier by bind) or "other:<Label>".
path is a list of [RELATIONSHIP, "out"|"in"] with 1 or 2 hops.
target is {{"label": L, "props": {{...}}}} or {{"role": name}}.
Allowed labels: {sorted(LABELS)}
Allowed relationships: {sorted(RELATIONSHIPS)}
Filters ("props", "all_targets", attribute_equals) may ONLY use these properties and values:
{json.dumps({k: sorted(map(str, v)) for k, v in VOCAB.items()})}  (active is true/false)
"kind" values depend on the label: {json.dumps({k: sorted(v) for k, v in KIND_BY_LABEL.items()})}
Relationships connect only these labels (from -> to): {json.dumps(ENDS)}
For example a plan's alerts are reached as Plan -TARGETS-> System -ALERTS_TO-> Channel.
Never filter on names or titles. "other:<Label>" starts are only for a "present" condition that
binds a role; conditions about the plan's own things start at "anchor" or a bound "role:".
Example conditions (a toy library domain, shape only):
{{"id": "C1", "text": "A loan has exactly one automated reminder", "kind": "count_equals",
  "start": "anchor", "path": [["GATED_BY", "out"]], "target": {{"label": "Check"}}, "n": 1,
  "all_targets": {{"kind": "automated"}}, "citations": [...]}}
{{"id": "C2", "text": "Nobody active watches the desk inbox", "kind": "absent",
  "start": "role:ch", "path": [["WATCHES", "in"]],
  "target": {{"label": "Person", "props": {{"active": true}}}}, "citations": [...]}}
"all_targets" and "props" are always objects; "completion" must equal one condition's "id".
The completion step is the plan's final ACTION that turns the risk into the failure, usually
a step the plan takes (for example a rollout to every target: a "present" condition on a Step),
not a background state such as a missing owner. Include it even if the post-mortem mentions it
only once, and quote the sentence that describes it.
Rules: at least one "absent" condition; "completion" names the final step that completes
the failure; every condition has "citations": [{{"doc": "{doc_id}", "quote": "<a sentence copied
EXACTLY from the post-mortem>"}}]. Never invent or paraphrase a quote.

Output JSON with keys: id ("{lesson_id}"), name, origin ("synthetic"), summary, safe_pattern,
learned_from (list), completion, conditions (each with id, text, kind, the kind's fields, citations).

POST-MORTEM ({doc_id}):
{doc_text}
"""


def _problems(reply, sources):
    try:
        lesson = Lesson.model_validate(json.loads(reply))
    except (json.JSONDecodeError, ValidationError) as e:
        return None, [f"invalid shape: {str(e)[:300]}"]
    try:
        check_compiles(lesson)
    except (CompileError, KeyError) as e:
        return None, [f"does not compile: {e}"]
    bad = unverified_quotes(lesson, sources)
    return lesson, [f"{c}: {problem} ({doc})" for c, doc, problem in bad]


def propose_lesson(llm, doc_id, doc_text, sources, lesson_id, retries=2):
    prompt = build_prompt(doc_id, doc_text, lesson_id)
    replies = []
    for _ in range(retries + 1):
        reply = llm.complete_json(prompt)
        replies.append(reply)
        lesson, problems = _problems(reply, sources)
        if not problems:
            return lesson
        prompt = (build_prompt(doc_id, doc_text, lesson_id)
                  + "\nYOUR PREVIOUS DRAFT WAS REJECTED:\n- " + "\n- ".join(problems)
                  + "\nFix every problem. Copy quotes exactly.\n")
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    (QUARANTINE / f"{lesson_id}.json").write_text(json.dumps(
        {"doc": doc_id, "replies": replies, "problems": problems}, indent=2))
    raise ProposalRejected(f"{lesson_id}: rejected after {retries + 1} drafts: {problems}")
