"""Shared UI helpers: the cached connection, the error guard, the look. No Cypher here."""
import streamlit as st
from redis.exceptions import ConnectionError as DBConnectionError

from nodus.db import get_graph

LEVEL_WORDS = {"full": "Full echo", "foresight": "One step away", "strong": "Strong echo",
               "note": "Note", "ignore": "Quiet"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap');
html, body, [class*="st-"], .stMarkdown, button, input, textarea, select {
  font-family: 'Atkinson Hyperlegible', system-ui, sans-serif !important; }
.block-container { max-width: 1040px; padding-top: 2.2rem; }
h1 { font-size: 2.05rem; line-height: 1.15; letter-spacing: -0.01em; font-weight: 700; }
h2 { font-size: 1.35rem; font-weight: 700; margin-top: 1.6rem; }
h3 { font-size: 1.1rem; font-weight: 700; }
p, li { max-width: 72ch; line-height: 1.55; }
.ledger-row { border-top: 1px solid #CBD3D0; padding: 0.9rem 0 0.6rem; }
.ledger-title { font-size: 1.12rem; font-weight: 700; }
.ledger-meta { color: #5D6A67; font-size: 0.92rem; }
.echo-line { display: grid; grid-template-columns: 112px 1fr 9.5rem; gap: 0.8rem;
  align-items: center; margin: 0.3rem 0; font-size: 0.97rem; }
.echo-line > span:last-child { white-space: nowrap; }
[data-testid="stIconMaterial"], .material-symbols-rounded {
  font-family: 'Material Symbols Rounded' !important; }
.lvl-foresight, .lvl-full { color: #B42318; font-weight: 700; }
.lvl-strong { color: #8A4B12; font-weight: 700; }
.lvl-note, .lvl-ignore { color: #5D6A67; }
.silence { color: #6E64A0; }
.quote { border-left: 3px solid #CBD3D0; padding-left: 0.8rem; color: #33413F; font-style: italic; }
.synthetic-tag { color: #5D6A67; font-size: 0.85rem; }
:focus-visible { outline: 3px solid #2E7A68 !important; outline-offset: 2px; }
</style>
"""


@st.cache_resource
def graph():
    return get_graph()


def setup(title):
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        graph().ro_query("RETURN 1")
    except DBConnectionError:
        st.error("NODUS can't reach FalkorDB on localhost:6379. Start it with "
                 "`docker compose up -d` in the project folder, then reload this page.")
        st.stop()
    return graph()


def level_html(level):
    return f'<span class="lvl-{level}">{LEVEL_WORDS[level]}</span>'


def open_echo(plan_id, lesson_id):
    st.session_state["echo_target"] = (plan_id, lesson_id)
    st.switch_page("app_pages/echo.py")
