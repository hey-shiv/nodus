"""Generate the evaluation families (eval/DECLARATION.md) as world data for one split.

Each plan: {"id", "family", "target", "expect", "text"} plus its graph structure.
"""
import random

from nodus.world import _World

FRESH_NOUNS = ["greenhouse irrigation schedule", "library loan reminders", "bakery oven timers",
               "museum audio guide", "school bus roster", "clinic appointment slots",
               "farm milk cooling log", "theatre seat map", "harbour crane booking",
               "bike share docking rules", "orchard picking rota", "ferry timetable feed"]
FRESH_VERBS = ["Refresh", "Rework", "Swap out", "Tidy", "Rebuild", "Reprice", "Retune", "Rename"]

KEYWORDS = {   # the vocabulary a reader associates with each lesson's post-mortems
    "antibody-1": ["global rule change", "content update", "staged rollout", "channel file",
                   "sensor template", "validator", "regular expression", "SOP"],
    "antibody-2": ["automated emails", "cronjob notifications", "error emails", "backups",
                   "router deployment", "DMARC", "alert messages", "order router"],
    "internal-quiet-push": ["firmware push", "label printers", "every depot", "canary batch",
                            "printer alerts", "email list", "depot staff", "firmware"],
}

CONDITIONS = {   # which plan attributes make each lesson's conditions hold
    "antibody-1": ["routine", "procedure_exists", "skips_procedure", "single_auto_gate", "rollout_all"],
    "antibody-2": ["has_channel", "email_channel", "unwatched", "goes_live"],
    "internal-quiet-push": ["procedure_exists", "skips_procedure", "has_channel", "unwatched",
                            "rollout_all"],
}
IDS = {"antibody-1": ["A1.1", "A1.2", "A1.3", "A1.4", "A1.5"],
       "antibody-2": ["A2.1", "A2.2", "A2.3", "A2.4"],
       "internal-quiet-push": ["Q.1", "Q.2", "Q.3", "Q.4", "Q.5"]}
COMPLETION = {"antibody-1": "A1.5", "antibody-2": "A2.4", "internal-quiet-push": "Q.5"}
DROPPABLE = {"routine", "skips_procedure", "single_auto_gate", "rollout_all", "email_channel",
             "unwatched", "goes_live"}     # neither company-level nor role-binders

SAFE = {"routine": False, "skips_procedure": False, "single_auto_gate": False,
        "rollout_all": False, "email_channel": False, "unwatched": False, "goes_live": True}


def risky(lesson):
    attrs = dict(SAFE)
    for a in CONDITIONS[lesson]:
        if a in attrs:
            attrs[a] = True
    return attrs


def drop(attrs, attr):
    out = dict(attrs)
    out[attr] = not out[attr] if attr != "goes_live" else False
    if attr == "goes_live":
        out["rollout_all"] = False
    return out


def fresh_text(rng):
    return f"{rng.choice(FRESH_VERBS)} the {rng.choice(FRESH_NOUNS)}", \
        f"Update to the {rng.choice(FRESH_NOUNS)} planned for next week."


def keyword_text(rng, lesson):
    kw = rng.sample(KEYWORDS[lesson], 4)
    return f"{kw[0].capitalize()} for the {kw[1]}", f"Ships the {kw[2]} and checks {kw[3]}."


def _add_plan(w, pid, title, summary, attrs):
    w.node("Plan", pid, title=title, summary=summary, status="planned",
           risk_class="routine" if attrs["routine"] else ("standard" if attrs.get("risk_known", True) else None),
           change_type="config_change")
    if attrs.get("risk_known", True) is False:
        w.nodes[-1]["props"].pop("risk_class")
    sys_id, ch_id = f"{pid}-sys", f"{pid}-ch"
    w.node("System", sys_id, name=f"{title} system")
    w.node("Channel", ch_id, kind="email_list" if attrs["email_channel"] else "pager",
           title=f"{title} alerts")
    w.rel("TARGETS", pid, sys_id)
    w.rel("ALERTS_TO", sys_id, ch_id)
    if not attrs["unwatched"]:
        w.rel("WATCHES", "ev-oncall", ch_id)
    if not attrs["skips_procedure"]:
        w.rel("FOLLOWS", pid, "ev-proc")
    w.rel("GATED_BY", pid, "ev-auto")
    if not attrs["single_auto_gate"]:
        w.rel("GATED_BY", pid, "ev-human")
    if attrs["goes_live"]:
        step = w.node("Step", f"{pid}-go", kind="rollout",
                      scope="all" if attrs["rollout_all"] else "subset", at=1_800_000_000)
        w.rel("HAS_STEP", pid, step)


def generate(seed):
    rng = random.Random(seed)
    w = _World()
    w.node("Document", "doc-world-tern-tally", title="Evaluation company (synthetic)")
    w.node("Person", "ev-oncall", name="On-call engineer", active=True)
    w.node("Procedure", "ev-proc", kind="staged_rollout", title="Staged rollout")
    w.node("Check", "ev-auto", kind="automated", title="Automated check")
    w.node("Check", "ev-human", kind="human", title="Human review")
    for i in range(5):
        w.node("Plan", f"ev-bg{i}", title=f"Background change {i}", status="done")
        w.rel("FOLLOWS", f"ev-bg{i}", "ev-proc")

    plans = []

    def plan(family, target, attrs, text, expect):
        pid = f"{family.lower()}-{len(plans):03d}"
        _add_plan(w, pid, *text, attrs)
        plans.append({"id": pid, "family": family, "target": target, "expect": expect,
                      "text": " ".join(text)})

    for lesson in CONDITIONS:
        for i in range(6):
            attrs = risky(lesson)
            if i % 2:
                attrs = drop(attrs, {"A1.5": "rollout_all", "A2.4": "goes_live",
                                     "Q.5": "rollout_all"}[COMPLETION[lesson]])
            plan("F1", lesson, attrs, fresh_text(rng), "raised")
        for _ in range(6):
            attrs = dict(SAFE)
            attrs[rng.choice(["routine", "rollout_all", "single_auto_gate"])] = True
            plan("F2", lesson, attrs, keyword_text(rng, lesson), "quiet")
        for attr, cid in zip(CONDITIONS[lesson], IDS[lesson]):
            if attr in DROPPABLE:
                for _ in range(2):
                    plan("F3", lesson, drop(risky(lesson), attr), fresh_text(rng), cid)
    for _ in range(10):
        plan("F4", None, dict(SAFE), fresh_text(rng), "quiet")
    full_a1 = risky("antibody-1")
    plan("F5", "antibody-1", full_a1, ("Update the footer copyright year",
                                       "Change 2025 to 2026 in the website footer."), "a")
    no_risk = dict(full_a1, risk_known=False)
    plan("F5", "antibody-1", no_risk, fresh_text(rng), "b")
    partial = dict(full_a1, rollout_all=False)
    plan("F5", "antibody-1", partial, fresh_text(rng), "c")
    return {"nodes": w.nodes, "rels": w.rels}, plans
