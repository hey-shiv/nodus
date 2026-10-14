"""How it works: the method in plain words, and what the demo is and isn't."""
import streamlit as st

from app_pages.common import setup

setup("How it works")
st.title("How NODUS works")
st.markdown("""
Companies repeat failures, even ones they wrote down, because people (and search tools) look
for lessons by what things *sound* like. NODUS stores each lesson as a pattern of **roles and
relationships** in a FalkorDB graph, and checks every plan against it.

**A lesson** is three to six conditions, such as "this change does not follow the staged
procedure other changes follow". Each condition quotes the sentence it comes from: a public
post-mortem, or the company's own. A person approves every lesson before it is used.

**Matching** runs one small graph query per condition, starting from the plan. It counts how many
hold (k of n) and keeps "the channel" or "the procedure" the same entity across conditions.
If all but the lesson's final step hold, the plan is **one step away**, and NODUS names that step.

**Silence** is something the lesson expects but the graph doesn't contain, such as nobody watching
an alert channel. NODUS words it as "not recorded in the company graph", because it can only see
what was recorded.

**Witnesses** are invited by their role in the original episode: first someone who raised a concern
that was overruled, then the post-mortem's author, then the owner of the system. Public lessons
cite their documents instead of people. Nobody is scored or ranked.

**What the AI does and doesn't do.** An AI model may *draft* a lesson from a post-mortem; the draft
must pass automatic checks and a human approval. The AI never writes the queries that run, never
decides a match or its severity, and never approves anything. Every sentence NODUS shows is filled
in from match results.

**This demo** uses Tern & Tally Freight, a fictional company. Real companies appear only as cited
sources: Cloudflare (2019), CrowdStrike (2024), Knight Capital (2012, via the U.S. SEC) and GitLab
(2017). NODUS flags structural resemblance to approved lessons; it doesn't predict incidents.
""")
