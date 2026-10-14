"""Inbox: heads-ups for plan owners and invitations for witnesses, with acknowledgement."""
import streamlit as st

from app_pages.common import level_html, open_echo, setup
from nodus.agent import acknowledge, messages_for
from nodus.plans import people

g = setup("Inbox")
everyone = {pid: name for pid, name, active in people(g) if active}
default = "p-lena" if "p-lena" in everyone else next(iter(everyone))
who = st.selectbox("Viewing as", list(everyone), format_func=everyone.get,
                   index=list(everyone).index(st.session_state.get("viewer", default)))
st.session_state["viewer"] = who

msgs = messages_for(g, who)
st.title(f"{everyone[who]}'s inbox")
if not msgs:
    st.write("Nothing here. NODUS writes when a plan this person owns echoes a lesson, or when "
             "they're invited as a witness.")
    st.stop()

for (eid, pid, ptitle, lid, lname, origin, lvl, k, n, headsup, silences, status, outcome,
     reason, is_owner) in msgs:
    st.markdown('<div class="ledger-row"></div>', unsafe_allow_html=True)
    role = "Heads-up on your plan" if is_owner else "You're invited as a witness"
    st.markdown(f"**{role}: {ptitle}**  \n{level_html(lvl)} {k} of {n} conditions of "
                f"“{lname}” ({'public' if origin == 'public' else 'internal'} lesson)",
                unsafe_allow_html=True)
    st.write(headsup)
    for s in silences or []:
        st.markdown(f'<div class="silence">{s}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4])
    if c1.button("Open echo", key=f"open-{eid}"):
        open_echo(pid, lid)
    if outcome:
        c2.caption(f"Recorded: {outcome}" + (f" ({reason})" if reason else ""))
    elif is_owner:
        with c2.form(f"ack-{eid}"):
            choice = st.radio("What will you do?", ["heeded", "dismissed", "escalated"],
                              horizontal=True, format_func={
                                  "heeded": "Change the plan", "dismissed": "Dismiss",
                                  "escalated": "Escalate"}.get)
            why = st.text_input("Reason (needed to dismiss)")
            if st.form_submit_button("Record my answer"):
                try:
                    acknowledge(g, eid, everyone[who], choice, why)
                    st.rerun()
                except ValueError as e:
                    st.error(f"Not recorded: {e}.")
    else:
        c2.caption("Witnesses advise; the plan owner records what happens.")
