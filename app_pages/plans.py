"""Plans: what NODUS is watching, and the owner's edits that make it react."""
import streamlit as st

from app_pages.common import level_html, open_echo, setup
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
    st.markdown(f'<div class="ledger-row"><div class="ledger-title">{title}</div>'
                f'<div class="ledger-meta">Owner: {owner or "none recorded"}, filed as {risk}'
                f'</div></div>', unsafe_allow_html=True)
    if summary:
        st.caption(summary)
    for les in lessons:
        r, lvl = results[(pid, les["id"])]
        if lvl == "ignore":
            continue
        states = [(c.holds, spec["kind"] == "absent") for c, spec in zip(r.conditions, les["conditions"])]
        comp = [c["id"] for c in les["conditions"]].index(les["completion"])
        origin = "public" if les["origin"] == "public" else "internal"
        cols = st.columns([6, 1.2], vertical_alignment="center")
        cols[0].markdown(f'<div class="echo-line"><span>{shape_strip(states, comp)}</span>'
                         f'<span>{r.k} of {r.n}: “{les["name"]}” ({origin})</span>'
                         f'{level_html(lvl)}</div>', unsafe_allow_html=True)
        if is_warning(lvl) and cols[1].button("Open echo", key=f"open-{pid}-{les['id']}"):
            open_echo(pid, les["id"])

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

if "last_save" in st.session_state:
    name, raised = st.session_state["last_save"]
    if raised:
        st.warning(f"Saved “{name}”. NODUS raised: " +
                   "; ".join(f"{lname} ({lvl})" for lname, lvl in raised))
    else:
        st.success(f"Saved “{name}”. No lesson echoes this plan now.")
