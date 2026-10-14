"""Optional: Laya (github.com/NandhaKishorM/laya) suggests roles and sorts dismissal reasons.

Two jobs, both advisory:
1. suggest_roles(): read a plan's text and *suggest* its controlled-vocabulary roles.
   Suggestions are stored apart from the real roles (Plan.suggested_*). The matcher never
   reads them. Only confirm_role(), called by a person, copies a value into the real role.
   This keeps words out of the structure-only decision: a plan that merely *sounds* risky
   can't change any match until someone confirms what is true.
2. categorise_reason(): sort a free-text dismissal reason into a fixed category, so a lesson's
   track record can show "dismissed 4 times, 3 of them as 'already mitigated elsewhere'".

Laya is imported lazily. If it isn't installed, available() is False and NODUS works as before.
"""
import time

from nodus.db import read

RISK_CRITERIA = {
    "routine": "a regular, repeated change done many times before, treated as low risk",
    "standard": "a normal change that needs the usual planning and review",
    "high": "an unusual, large or risky change that needs extra care",
}
CHANGE_TYPE_CRITERIA = {
    "config_change": "changing settings, tables, rules or configuration data",
    "code_deploy": "shipping new software, firmware or a code patch",
    "infra_change": "changing providers, servers, networks or infrastructure",
    "data_migration": "moving, converting or cutting over data between systems",
}
REASON_CRITERIA = {
    "mitigated_elsewhere": "the risk is already covered by another check, team or safeguard",
    "does_not_apply": "the lesson does not fit this plan; the situation is different",
    "accepted_low_stakes": "the risk is real but small enough to accept",
    "other": "anything else",
}
ROLE_CRITERIA = {"risk_class": RISK_CRITERIA, "change_type": CHANGE_TYPE_CRITERIA}

_router = None


def available():
    try:
        import laya  # noqa: F401
        return True
    except ImportError:
        return False


def laya_predict(state, questions):
    """The real call: one forward pass of Laya's router (downloads a checkpoint on first use)."""
    global _router
    if _router is None:
        from laya import Router
        _router = Router()
    return _router.predict(state, questions)


def _ask(predict, state, qid, instructions, criteria):
    result = predict(state, {qid: {"type": "choice", "instructions": instructions,
                                   "criteria": criteria}})
    answer = result["answers"][qid]
    return answer["choice"], float(answer.get("confidence", 0.0))


def suggest_roles(plan_text, predict=laya_predict):
    """{role: (label, confidence)} for each controlled-vocabulary role, from text only."""
    return {
        "risk_class": _ask(predict, plan_text, "risk_class",
                           "How risky is this planned change, as its team would file it?", RISK_CRITERIA),
        "change_type": _ask(predict, plan_text, "change_type",
                            "What kind of change is this?", CHANGE_TYPE_CRITERIA),
    }


def categorise_reason(reason, predict=laya_predict):
    return _ask(predict, reason, "reason",
                "Why was this warning about a plan dismissed?", REASON_CRITERIA)


def store_suggestions(graph, plan_id, suggestions, now=None):
    """Write suggestions beside, never over, the plan's real roles."""
    sets, params = [], {"id": plan_id, "at": now or int(time.time())}
    for role, (label, conf) in suggestions.items():
        if role not in ROLE_CRITERIA or label not in ROLE_CRITERIA[role]:
            raise ValueError(f"not an allowed suggestion: {role}={label}")
        sets += [f"p.suggested_{role} = ${role}", f"p.suggested_{role}_conf = ${role}_conf"]
        params[role], params[f"{role}_conf"] = label, conf
    graph.query(f"MATCH (p:Plan {{id: $id}}) SET {', '.join(sets)}, "
                f"p.suggested_by = 'laya', p.suggested_at = $at", params)


def suggestions_for(graph, plan_id):
    rows = read(graph, "MATCH (p:Plan {id: $id}) RETURN p.risk_class, p.suggested_risk_class, "
                       "p.suggested_risk_class_conf, p.change_type, p.suggested_change_type, "
                       "p.suggested_change_type_conf", {"id": plan_id})
    if not rows or rows[0][1] is None:
        return {}
    rc, src, srcc, ct, sct, sctc = rows[0]
    return {"risk_class": {"recorded": rc, "suggested": src, "confidence": srcc},
            "change_type": {"recorded": ct, "suggested": sct, "confidence": sctc}}


def confirm_role(graph, plan_id, role, value, by, now=None):
    """The human step: only this makes a suggested value part of the structure."""
    if role not in ROLE_CRITERIA or value not in ROLE_CRITERIA[role]:
        raise ValueError(f"not an allowed role value: {role}={value}")
    graph.query(f"MATCH (p:Plan {{id: $id}}) SET p.{role} = $value, "
                f"p.{role}_confirmed_by = $by, p.{role}_confirmed_at = $at",
                {"id": plan_id, "value": value, "by": by, "at": now or int(time.time())})
