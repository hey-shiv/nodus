"""NODUS: learn from mistakes you never made.  Run:  streamlit run app.py"""
import streamlit as st

from app_pages.common import graph
from nodus.agent import observe_all
from scripts.setup_demo import build

st.set_page_config(page_title="NODUS", page_icon="◌", layout="wide")

pages = st.navigation([
    st.Page("app_pages/plans.py", title="Plans", default=True),
    st.Page("app_pages/echo.py", title="Echo"),
    st.Page("app_pages/inbox.py", title="Inbox"),
    st.Page("app_pages/lessons.py", title="Lessons"),
    st.Page("app_pages/about.py", title="How it works"),
])

with st.sidebar:
    st.markdown('<div class="brand">NODUS</div>', unsafe_allow_html=True)
    st.markdown('<dl class="spec"><dt>Type</dt><dd>Immune memory for plans</dd>'
                '<dt>Engine</dt><dd>FalkorDB graph patterns</dd>'
                '<dt>Company</dt><dd>Tern &amp; Tally Freight (synthetic)</dd></dl>',
                unsafe_allow_html=True)
    st.caption("Learn from mistakes you never made.")
    with st.expander("Reset the demo"):
        approved = st.checkbox("Lessons already approved", value=True)
        if st.button("Reset demo world", type="secondary"):
            build(graph(), "Shivashant (builder)" if approved else None)
            observe_all(graph())
            st.session_state.clear()
            st.toast("Demo world reloaded.")
            st.rerun()

pages.run()
