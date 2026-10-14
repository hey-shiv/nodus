"""Echo: the past failure's shape beside the plan, condition by condition."""
import streamlit as st

from app_pages.common import level_html, setup
from nodus.agent import echo_id, echo_record
from nodus.lessons import active_lessons, lesson_detail
from nodus.matcher import evaluate
from nodus.plans import list_plans
from nodus.severity import level
from nodus.svg import alignment_svg
from nodus.view import rows_for
from nodus.witnesses import route

g = setup("Echo")
lessons = {l["id"]: l for l in active_lessons(g)}
plans = {p[0]: p[1] for p in list_plans(g)}
if not lessons or not plans:
    st.title("Nothing to compare yet")
    st.write("Approve a lesson on the Lessons page, then open an echo from the Plans page.")
    st.stop()

plan_id, lesson_id = st.session_state.get("echo_target", ("plan-hero", "antibody-1"))
c1, c2 = st.columns(2)
plan_id = c1.selectbox("Plan", list(plans), format_func=plans.get,
                       index=list(plans).index(plan_id) if plan_id in plans else 0)
lesson_id = c2.selectbox("Lesson", list(lessons), format_func=lambda i: lessons[i]["name"],
                         index=list(lessons).index(lesson_id) if lesson_id in lessons else 0)
st.session_state["echo_target"] = (plan_id, lesson_id)

les = lessons[lesson_id]
result = evaluate(g, plan_id, les)
lvl = level(result.k, result.n, result.missing, les["completion"])
rows = rows_for(g, plan_id, les, result)

completion_text = next(c["text"] for c in les["conditions"] if c["id"] == les["completion"])
if lvl == "foresight":
    st.title(f"One step from “{les['name']}”")
    st.write(f"{result.k} of {result.n} conditions already hold. The remaining one is the step "
             f"that would complete the failure: **{completion_text.lower()}**.")
elif lvl == "full":
    st.title(f"“{plans[plan_id]}” has the whole shape of “{les['name']}”")
    st.write("Every condition holds, including the final step.")
else:
    st.title(f"{result.k} of {result.n} conditions of “{les['name']}”")
    st.markdown(f"Level: {level_html(lvl)}", unsafe_allow_html=True)

st.markdown(alignment_svg(les["name"], plans[plan_id], rows, result.k, result.n, lvl),
            unsafe_allow_html=True)
st.caption("Green ✓ holds in the plan. Violet ∅ is something not recorded in the company graph. "
           "The dashed red ring is the completion step. Grey means not present.")

record = echo_record(g, echo_id(lesson_id, plan_id))
st.header("What NODUS told the owner")
if record and record[0]:
    headsup, silences, status, outcome, seen = record
    st.write(headsup)
    for s in silences or []:
        st.markdown(f'<div class="silence">{s}</div>', unsafe_allow_html=True)
    st.caption(f"Status: {status}" + (f", outcome: {outcome}" if outcome else "") +
               f". Seen on {seen} save{'s' if seen != 1 else ''}.")
else:
    st.write("No heads-up recorded for this pair. NODUS writes one when a plan is saved and "
             "the echo is at warning level.")

if les["origin"] == "public":
    st.header("Where this lesson comes from")
    st.write("Public post-mortems. The witnesses are the documents themselves: NODUS never "
             "contacts people at other companies.")
else:
    st.header("Who saw it coming")
    w = route(g, lesson_id, plan_id)
    st.write(f"Invited: **{w.name}**, who {w.reason}. An invitation asks for advice; it is not a "
             "verdict on anyone." if w else "No witness available.")

with st.expander("Every condition, with its source sentence"):
    for c in lesson_detail(g, lesson_id):
        st.markdown(f"**{c['id']}** {c['text']}")
        for cit in c["citations"]:
            link = f" ([source]({cit['url']}))" if cit.get("url") else ""
            st.markdown(f'<div class="quote">“{cit["quote"]}”</div>', unsafe_allow_html=True)
            st.caption(f"{cit['publisher']}: {cit['title']}{link}")
