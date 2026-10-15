"""Plans: what NODUS is watching, and the owner's edits that make it react."""
import streamlit as st

from app_pages.common import level_html, open_echo, setup, spec
from nodus.agent import on_plan_saved
from nodus.lessons import active_lessons
from nodus.matcher import evaluate
from nodus.plans import add_step, list_plans, plan_facts, remove_step, set_follows, set_gate
from nodus.severity import is_warning, level
from nodus.svg import shape_strip

g = setup("Plans")
lessons = active_lessons(g)
plans = list_plans(g)

results = {}
for pid, *_ in plans:
    for les in lessons:
        r = evaluate(g, pid, les)
        results[(pid, les["id"])] = (r, level(r.k, r.n, r.missing, les["completion"]))

at_risk = {pid for (pid, _), (_, lvl) in results.items() if is_warning(lvl)}
one_step = {pid for (pid, _), (_, lvl) in results.items() if lvl == "foresight"}

if not lessons:
    st.title("No lessons are active yet")
    st.write("NODUS only watches plans against approved lessons. Approve one on the Lessons page.")
    st.page_link("app_pages/lessons.py", label="Review lessons")
    st.stop()

full = {pid for (pid, _), (_, lvl) in results.items() if lvl == "full"}
if one_step:
    st.title(f"{len(one_step)} of {len(plans)} plans {'is' if len(one_step) == 1 else 'are'} "
             f"one step from a known failure")
elif full:
    st.title(f"{len(full)} of {len(plans)} plans {'has' if len(full) == 1 else 'have'} "
             f"the whole shape of a known failure")
else:
    st.title("No plan echoes a known failure right now")
st.write(f"NODUS checks every plan against {len(lessons)} approved lessons by structure: who "
         f"and what is connected, not which words are used. {len(at_risk)} plans need attention.")

for pid, title, summary, risk, owner in sorted(plans, key=lambda p: (p[0] not in at_risk, p[1])):
    st.markdown(f'<div class="ledger-row"><div class="ledger-title">{title}</div></div>',
                unsafe_allow_html=True)
    spec([("Owner", owner or "none recorded", False), ("Filed as", risk, False),
          ("Note", summary or "none", False)])
    for les in lessons:
        r, lvl = results[(pid, les["id"])]
        if lvl == "ignore":
            continue
        states = [(c.holds, spec["kind"] == "absent") for c, spec in zip(r.conditions, les["conditions"])]
        comp = [c["id"] for c in les["conditions"]].index(les["completion"])
        origin = "public" if les["origin"] == "public" else "internal"
        cols = st.columns([6, 1.2], vertical_alignment="center")
        cols[0].markdown(f'<div class="echo-line"><span>{shape_strip(states, comp)}</span>'
                         f'<span><span class="kn">{r.k} OF {r.n}</span>&nbsp; “{les["name"]}” '
                         f'<span class="label">{origin}</span></span>'
                         f'{level_html(lvl)}</div>', unsafe_allow_html=True)
        if is_warning(lvl) and cols[1].button("Open echo", key=f"open-{pid}-{les['id']}"):
            open_echo(pid, les["id"])

with st.expander("Compare with keyword search"):
    from pathlib import Path

    from nodus.baseline import keyword_ranking
    from nodus.lessons import load_lesson_file
    files = sorted((Path(__file__).resolve().parent.parent / "data" / "lessons").glob("*.json"))
    names = {les["id"]: les["name"] for les in lessons}
    st.write("A keyword search ranks plans by how much their words overlap a lesson's text "
             "(TF-IDF similarity; the evaluation's baseline). NODUS ignores the words and checks "
             "the structure.")
    table = []
    for rpid, rlid, sim in keyword_ranking([load_lesson_file(f) for f in files],
                                          [(p[0], p[1], p[2]) for p in plans]):
        raised = [names[l] for (pp, l), (_, lvl) in results.items() if pp == rpid and is_warning(lvl)]
        table.append({"Plan": next(p[1] for p in plans if p[0] == rpid),
                      "Closest lesson by words": names.get(rlid, rlid),
                      "Word similarity": round(sim, 3),
                      "NODUS raises": ", ".join(raised) or "nothing"})
    st.dataframe(table, hide_index=True, use_container_width=True)

st.header("Change a plan")
st.write("Edit a plan as its owner would. Saving runs NODUS on the plan straight away.")
titles = {pid: title for pid, title, *_ in plans}
pid = st.selectbox("Plan", list(titles), format_func=titles.get,
                   index=list(titles).index("plan-hero") if "plan-hero" in titles else 0)
facts = plan_facts(g, pid)
st.markdown("**Steps:** " + ("; ".join(
    f"{kind}" + (" to every target" if scope == "all" else f" ({scope})")
    for _, kind, scope, _ in facts["steps"]) or "none yet"))

with st.form("edit-plan"):
    c1, c2 = st.columns(2)
    follows = c1.checkbox("Follows the canary procedure",
                          value=any(p == "proc-canary" for p, _ in facts["follows"]))
    reviewed = c1.checkbox("Peer review sign-off before release",
                           value=any(c == "chk-human" for c, *_ in facts["gates"]))
    new_kind = c2.radio("Add a step", ["(none)", "canary", "test", "review", "rollout"],
                        horizontal=True, format_func=lambda k: "nothing" if k == "(none)" else k)
    new_scope = c2.radio("Scope of the new step", ["subset", "all"], horizontal=True,
                         format_func={"subset": "some targets", "all": "every target"}.get)
    removable = {sid: f"{kind} ({'every target' if scope == 'all' else scope})"
                 for sid, kind, scope, _ in facts["steps"]}
    drop = c2.multiselect("Remove steps", list(removable), format_func=removable.get)
    saved = st.form_submit_button("Save plan", type="primary")

if saved:
    set_follows(g, pid, "proc-canary", follows)
    set_gate(g, pid, "chk-human", reviewed)
    for sid in drop:
        remove_step(g, sid)
    if new_kind != "(none)":
        add_step(g, pid, new_kind, new_scope)
    report = on_plan_saved(g, pid)
    st.session_state["last_save"] = (titles[pid], [(r["lesson_name"], r["level"]) for r in report])
    st.rerun()

with st.expander("Suggest roles from the plan's text (optional: Laya)"):
    from nodus import suggest
    st.write("NODUS matches on recorded roles such as the risk class. Laya, a small local "
             "classifier, can read the plan's text and *suggest* them. A suggestion changes "
             "nothing until the owner confirms it, so a plan that only sounds risky can't "
             "change a match.")
    if not suggest.available():
        st.caption("Laya isn't installed. To try it: `uv pip install --python .venv/bin/python "
                   "-r requirements-laya.txt` (downloads about 1.7 GB on first use).")
    else:
        plan_row = next(p for p in plans if p[0] == pid)
        if st.button("Suggest roles", key=f"suggest-{pid}"):
            with st.spinner("Laya is reading the plan…"):
                suggest.store_suggestions(g, pid, suggest.suggest_roles(
                    f"{plan_row[1]}. {plan_row[2] or ''}"))
        for role, info in suggest.suggestions_for(g, pid).items():
            words = role.replace("_", " ")
            line = (f"**{words}**: recorded *{info['recorded'] or 'not recorded'}*, Laya suggests "
                    f"*{info['suggested']}* (confidence {info['confidence']:.2f})")
            if info["recorded"] == info["suggested"]:
                st.markdown(line + ": they agree.")
            else:
                c1, c2 = st.columns([4, 1])
                c1.markdown(line)
                if c2.button("Confirm", key=f"confirm-{pid}-{role}"):
                    owner = plan_row[4] or "plan owner"
                    suggest.confirm_role(g, pid, role, info["suggested"], owner)
                    report = on_plan_saved(g, pid)
                    st.session_state["last_save"] = (
                        titles[pid], [(r["lesson_name"], r["level"]) for r in report])
                    st.rerun()

if "last_save" in st.session_state:
    name, raised = st.session_state["last_save"]
    if raised:
        st.warning(f"Saved “{name}”. NODUS raised: " +
                   "; ".join(f"{lname} ({lvl})" for lname, lvl in raised))
    else:
        st.success(f"Saved “{name}”. No lesson echoes this plan now.")
