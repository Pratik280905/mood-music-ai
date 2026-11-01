r"""
MoodMuse AI — Multimodal Personalized Music Intelligence
Main Streamlit Application Entry Point.

To run:
    venv\Scripts\activate
    streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from ui.styles import get_custom_css
from ui.components import render_header, render_ethical_notice
from ui.pages import (
    render_generator_tab,
    render_trajectory_tab,
    render_dashboard_tab,
    render_profile_tab,
    render_diagnostics_tab
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MoodMuse AI — Multimodal Music Intelligence",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Custom Styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "current_emotion" not in st.session_state:
    st.session_state.current_emotion = None
if "current_context" not in st.session_state:
    st.session_state.current_context = None
if "current_recommendations" not in st.session_state:
    st.session_state.current_recommendations = []
if "current_journey" not in st.session_state:
    st.session_state.current_journey = None
if "active_source" not in st.session_state:
    st.session_state.active_source = "local_fallback"
if "source_note" not in st.session_state:
    st.session_state.source_note = ""
if "rated_ids" not in st.session_state:
    st.session_state.rated_ids = set()

# ---------------------------------------------------------------------------
# Header & Navigation Tabs
# ---------------------------------------------------------------------------
render_header(active_source=st.session_state.active_source)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎧 Emotion & Music Generator",
    "🌈 Emotional Journey Planner",
    "📊 Analytics Dashboard",
    "👤 User Taste & Profile",
    "⚙️ System Diagnostics & Viva"
])

with tab1:
    render_generator_tab()

with tab2:
    render_trajectory_tab()

with tab3:
    render_dashboard_tab()

with tab4:
    render_profile_tab()

with tab5:
    render_diagnostics_tab()

st.divider()
render_ethical_notice()