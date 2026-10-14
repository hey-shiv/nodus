"""Lessons: review each condition beside its source sentence, approve, see the track record."""
import streamlit as st

from app_pages.common import setup
from nodus.agent import track_record
from nodus.lessons import (approve, lesson_detail, list_lessons, load_sources, reject, store)

g = setup("Lessons")
rows = list_lessons(g)
st.title("Lessons NODUS watches for")
st.write("A lesson is a small set of conditions about roles and relationships. Each condition "
         "quotes the sentence it comes from. Nothing is matched until a person approves it.")
if not rows:
    st.write("No lessons stored. Reset the demo world from the sidebar.")
    st.stop()

status_words = {"approved": "Approved", "proposed": "Waiting for approval", "rejected": "Rejected"}
for lid, name, origin, status, version, approved_by in rows:
    st.markdown('<div class="ledger-row"></div>', unsafe_allow_html=True)
    st.subheader(name)
    st.caption(f"{'Public post-mortems' if origin == 'public' else 'Internal post-mortem (synthetic)'}"
               f", version {version}: {status_words.get(status, status)}"
               + (f" by {approved_by}" if approved_by and status == "approved" else ""))
    rec = track_record(g, lid)
    if rec["raised"]:
        st.write(f"Track record: raised {rec['raised']}, heeded {rec['heeded']}, dismissed "
                 f"{rec['dismissed']}, escalated {rec['escalated']}, open {rec['open']}.")
        for r in rec["reasons"]:
            st.caption(f"Dismissed because: {r}")
        if rec["reason_categories"]:
            names = {"mitigated_elsewhere": "already covered elsewhere",
                     "does_not_apply": "lesson doesn't apply", "accepted_low_stakes": "low stakes, accepted",
                     "other": "other"}
            st.caption("Laya's guess at the reasons (experimental: 2 of 6 right in our check; the reasons above are what counts): " + ", ".join(
                f"{names.get(c, c)} {n}" for c, n in rec["reason_categories"].items()))
    with st.expander("Conditions and sources", expanded=(status == "proposed")):
        for c in lesson_detail(g, lid):
            st.markdown(f"**{c['id']}** {c['text']}" + ("  ∅" if c["kind"] == "absent" else ""))
            for cit in c["citations"]:
                st.markdown(f'<div class="quote">“{cit["quote"]}”</div>', unsafe_allow_html=True)
                st.caption(f"{cit['publisher']}: {cit['title']}"
                           + (f" ([source]({cit['url']}))" if cit.get("url") else ""))
    if status != "approved":
        reviewer = st.text_input("Your name", value="Shivashant", key=f"who-{lid}")
        c1, c2 = st.columns([1, 5])
        if c1.button("Approve", key=f"ok-{lid}", type="primary"):
            approve(g, lid, reviewer)
            st.rerun()
        if c2.button("Reject", key=f"no-{lid}"):
            reject(g, lid, reviewer)
            st.rerun()

st.header("Draft a lesson from a post-mortem")
st.write("An AI model can draft a lesson from an internal post-mortem. The draft is checked "
         "automatically (shape, allowed names, every quote found word for word) and then waits "
         "here for approval. Needs a Gemini key in .env or a local Ollama model.")
sources = load_sources()
internal = {k: v for k, v in sources.items() if v["origin"] == "synthetic"}
doc = st.selectbox("Post-mortem", list(internal), format_func=lambda d: internal[d]["title"])
if st.button("Draft a lesson"):
    from pathlib import Path

    from nodus.llm import LLM, LLMError
    from nodus.proposals import ProposalRejected, propose_lesson
    text = (Path(__file__).resolve().parent.parent / internal[doc]["path"]).read_text()
    with st.spinner("Drafting and checking…"):
        try:
            lesson = propose_lesson(LLM(), doc, text, sources, f"draft-{doc}")
            store(g, lesson, sources)
            st.toast(f"Draft “{lesson.name}” passed every check and is waiting for approval.")
            st.rerun()
        except (LLMError, ProposalRejected) as e:
            st.error(f"No draft stored: {e}")
