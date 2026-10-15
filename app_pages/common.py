"""Shared UI helpers: the cached connection, the error guard, the look. No Cypher here.

The look is DESIGN.md ("Blueprint Ledger"); colours come from nodus/theme.py.
"""
from html import escape

import streamlit as st
from redis.exceptions import ConnectionError as DBConnectionError

from nodus.db import get_graph
from nodus.theme import COLORS as C

LEVEL_WORDS = {"full": "Full shape", "foresight": "One step away", "strong": "Strong echo",
               "note": "Note", "ignore": "Quiet"}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root {{
  --paper: {C["surface"]}; --tracing: {C["neutral"]}; --ink: {C["primary"]}; --deep: {C["on-surface"]};
  --pencil: {C["secondary"]}; --rule: {C["border"]}; --red: {C["tertiary"]}; --red-line: {C["tertiary-line"]};
  --oxide: {C["error"]};
  --display: Archivo, 'Helvetica Neue', Arial, sans-serif;
  --mono: 'IBM Plex Mono', ui-monospace, Menlo, monospace;
}}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, select, button,
[data-testid="stWidgetLabel"] {{ font-family: var(--display) !important; }}
.stApp {{ background: var(--paper); color: var(--deep); }}
[data-testid="stIconMaterial"], .material-symbols-rounded {{
  font-family: 'Material Symbols Rounded' !important; }}

/* the sheet: a hairline frame with registration crosses at the corners */
.block-container {{ max-width: 1080px; padding: 2.6rem 2.6rem 4rem; margin-top: 1.4rem;
  border: 1px solid var(--rule); position: relative;
  background:
    linear-gradient(var(--ink), var(--ink)) left 0 top 0 / 15px 1px no-repeat,
    linear-gradient(var(--ink), var(--ink)) left 7px top -7px / 1px 15px no-repeat,
    linear-gradient(var(--ink), var(--ink)) right 0 top 0 / 15px 1px no-repeat,
    linear-gradient(var(--ink), var(--ink)) right 7px top -7px / 1px 15px no-repeat; }}

/* type: uppercase grotesk sheet titles; mono labels; sentence case for everything people wrote */
h1 {{ font-family: var(--display) !important; font-weight: 800 !important; text-transform: uppercase;
  font-size: clamp(2rem, 4.4vw, 3.4rem) !important; line-height: 0.98 !important;
  letter-spacing: -0.03em; color: var(--ink); max-width: 18ch; text-wrap: balance; }}
h2 {{ font-family: var(--display) !important; font-weight: 800 !important; text-transform: uppercase;
  font-size: 1.6rem !important; letter-spacing: -0.02em; color: var(--ink);
  border-top: 1px solid var(--ink); padding-top: 1.1rem !important; margin-top: 2.4rem !important; }}
h3 {{ font-family: var(--display) !important; font-weight: 700 !important; font-size: 1.2rem !important;
  color: var(--ink); }}
p, li {{ max-width: 72ch; line-height: 1.6; }}
[data-testid="stCaptionContainer"], .stCaption {{ color: var(--pencil) !important; }}
.label {{ font-family: var(--mono); font-size: 0.75rem; font-weight: 500; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--pencil); }}

/* spec sheet: Heron's "TYPE : …" block */
.spec {{ display: grid; grid-template-columns: max-content 1fr; column-gap: 0.9rem; row-gap: 0.3rem;
  font-family: var(--mono); font-size: 0.82rem; line-height: 1.5; margin: 0.6rem 0 1rem;
  padding: 0.8rem 0; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }}
.spec dt {{ color: var(--pencil); text-transform: uppercase; letter-spacing: 0.08em; }}
.spec dt::after {{ content: " :"; }}
.spec dd {{ margin: 0; color: var(--ink); }}
.spec dd.red {{ color: var(--red); font-weight: 600; }}
@media (max-width: 640px) {{ .spec {{ grid-template-columns: 1fr; }} .spec dd {{ margin-bottom: 0.4rem; }} }}

/* ledger rows */
.ledger-row {{ border-top: 1px solid var(--ink); padding: 1.1rem 0 0.2rem; margin-top: 1rem; }}
.ledger-title {{ font-family: var(--display); font-size: 1.35rem; font-weight: 700; color: var(--ink);
  letter-spacing: -0.01em; }}
.echo-line {{ display: grid; grid-template-columns: 104px 1fr 10rem; gap: 0.9rem;
  align-items: center; margin: 0.35rem 0; font-size: 0.97rem; }}
.echo-line .kn {{ font-family: var(--mono); font-size: 0.85rem; color: var(--ink); }}
.lvl {{ font-family: var(--mono); font-size: 0.74rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; white-space: nowrap; }}
.lvl-foresight, .lvl-full {{ color: var(--red); }}
.lvl-strong {{ color: var(--ink); }}
.lvl-note, .lvl-ignore {{ color: var(--pencil); font-weight: 500; }}
@media (max-width: 640px) {{ .echo-line {{ grid-template-columns: 1fr; gap: 0.2rem; }} }}

.silence {{ color: var(--ink); font-family: var(--mono); font-size: 0.85rem;
  border-left: 1px dashed var(--ink); padding-left: 0.7rem; margin: 0.3rem 0; }}
.quote {{ background: var(--tracing); border-left: 2px solid var(--ink); padding: 0.7rem 1rem;
  color: var(--deep); margin: 0.4rem 0; }}

/* controls: square, graphite, mono labels; primary gets Heron's arrow cell */
.stButton > button, .stFormSubmitButton > button, [data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondaryFormSubmit"],
[data-testid="stBaseButton-primaryFormSubmit"] {{
  border-radius: 0 !important; font-family: var(--mono) !important; font-size: 0.78rem !important;
  letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid var(--ink) !important;
  box-shadow: none !important; min-height: 2.5rem; }}
.stButton > button p, .stFormSubmitButton > button p {{ font-family: var(--mono) !important; }}
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {{
  background: var(--ink) !important; color: var(--paper) !important; }}
[data-testid="stBaseButton-primary"]::after, [data-testid="stBaseButton-primaryFormSubmit"]::after {{
  content: "→"; margin-left: 0.9rem; padding-left: 0.9rem; border-left: 1px solid var(--paper); }}
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] {{
  background: var(--paper) !important; color: var(--ink) !important; }}
[data-testid="stBaseButton-secondary"]:hover {{ background: var(--tracing) !important; }}
input, textarea, [data-baseweb="select"] > div {{ border-radius: 2px !important; }}
[data-testid="stExpander"] details {{ border-radius: 0 !important; border-color: var(--rule) !important; }}
[data-testid="stForm"] {{ border-radius: 0 !important; border-color: var(--rule) !important; }}
[data-testid="stAlert"] {{ border-radius: 0 !important; }}

/* sidebar: the drawing's title block */
[data-testid="stSidebar"] {{ background: var(--tracing); border-right: 1px solid var(--rule); }}
[data-testid="stSidebarNav"] a span, [data-testid="stSidebarNavLink"] span {{
  font-family: var(--mono) !important; text-transform: uppercase; letter-spacing: 0.08em;
  font-size: 0.78rem; }}
[data-testid="stSidebarNavLink"] {{ border-radius: 0 !important; }}
.brand {{ font-family: var(--display); font-weight: 800; font-size: 1.6rem; letter-spacing: -0.02em;
  color: var(--ink); line-height: 1; }}

:focus-visible {{ outline: 2px solid var(--ink) !important; outline-offset: 2px; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
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
    return f'<span class="lvl lvl-{level}">{LEVEL_WORDS[level]}</span>'


def label(text):
    st.markdown(f'<div class="label">{escape(text)}</div>', unsafe_allow_html=True)


def spec(rows):
    """A spec sheet: [(label, value, red?)] rendered as LABEL : value lines."""
    items = "".join(f'<dt>{escape(k)}</dt><dd class="{"red" if red else ""}">{escape(str(v))}</dd>'
                    for k, v, red in rows)
    st.markdown(f'<dl class="spec">{items}</dl>', unsafe_allow_html=True)


def open_echo(plan_id, lesson_id):
    st.session_state["echo_target"] = (plan_id, lesson_id)
    st.switch_page("app_pages/echo.py")
