"""
Reusable UI Components for MoodMuse AI Streamlit application.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
import plotly.graph_objects as go
from config.settings import APP_NAME, APP_TAGLINE, APP_VERSION, ETHICAL_DISCLAIMER
from services.browser_service import open_url_in_browser
from services.spotify_service import spotify_service

def render_header(active_source: str = "local_fallback") -> None:
    """Renders the top application banner with active engine badge."""
    badge_html = (
        '<span class="mm-source-badge-spotify">🟢 Spotify Connected</span>'
        if active_source == "spotify" and spotify_service.is_connected
        else '<span class="mm-source-badge-fallback">⚡ Local AI Fallback Engine (135 Tracks)</span>'
    )

    st.markdown(
        f"""
        <div class="mm-hero-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <div class="mm-title">🎧 {APP_NAME}</div>
                    <div class="mm-tagline">{APP_TAGLINE} · v{APP_VERSION}</div>
                </div>
                <div>{badge_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_ethical_notice() -> None:
    """Displays required ethical & transparency disclaimer."""
    st.markdown(
        f"""
        <div class="mm-notice-banner">
            <strong>Ethical AI Transparency:</strong> {ETHICAL_DISCLAIMER}
        </div>
        """,
        unsafe_allow_html=True
    )

def create_radar_chart(distribution: Dict[str, float]) -> go.Figure:
    """Generates an emotion distribution radar chart."""
    categories = list(distribution.keys())
    values = [distribution[c] for c in categories]
    # Close the loop
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=[c.capitalize() for c in categories],
                fill="toself",
                fillcolor="rgba(167, 139, 250, 0.35)",
                line=dict(color="#a78bfa", width=2),
                marker=dict(size=5, color="#c084fc")
            )
        ]
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values) * 1.15 if values else 1.0], showticklabels=False),
            bgcolor="rgba(17, 24, 39, 0.6)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=35, t=25, b=25),
        height=260,
        showlegend=False,
        font=dict(color="#e5e7eb", size=11)
    )
    return fig

def create_circumplex_plot(valence: float, energy: float, emotion_label: str) -> go.Figure:
    """Generates a 2D Russell Circumplex Model scatter plot."""
    fig = go.Figure()

    # Four quadrants
    fig.add_shape(type="rect", x0=0, y0=0.5, x1=1, y1=1, fillcolor="rgba(34, 197, 94, 0.08)", line_width=0)
    fig.add_shape(type="rect", x0=-1, y0=0.5, x1=0, y1=1, fillcolor="rgba(239, 68, 68, 0.08)", line_width=0)
    fig.add_shape(type="rect", x0=-1, y0=0, x1=0, y1=0.5, fillcolor="rgba(59, 130, 246, 0.08)", line_width=0)
    fig.add_shape(type="rect", x0=0, y0=0, x1=1, y1=0.5, fillcolor="rgba(20, 184, 166, 0.08)", line_width=0)

    # Crosshairs
    fig.add_hline(y=0.5, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=0.0, line_dash="dot", line_color="rgba(255,255,255,0.2)")

    # User coordinate point
    fig.add_trace(
        go.Scatter(
            x=[valence],
            y=[energy],
            mode="markers+text",
            marker=dict(size=14, color="#f43f5e", line=dict(width=2, color="#ffffff")),
            text=[f"Current ({emotion_label})"],
            textposition="top center",
            textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans")
        )
    )

    fig.update_layout(
        xaxis=dict(title="Valence (Negative ➔ Positive)", range=[-1.05, 1.05], color="#9ca3af", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Energy (Low ➔ High)", range=[0.0, 1.05], color="#9ca3af", gridcolor="rgba(255,255,255,0.06)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17, 24, 39, 0.5)",
        margin=dict(l=40, r=30, t=25, b=35),
        height=260,
        showlegend=False,
        font=dict(color="#e5e7eb", size=10)
    )
    return fig

def render_emotion_dashboard(emotion_repr: Dict[str, Any]) -> None:
    """Renders the multimodal emotion metrics summary and visualization graphs."""
    prim = emotion_repr.get("primary_emotion", "neutral")
    conf = emotion_repr.get("confidence", 0.5)
    intensity = emotion_repr.get("intensity", 0.5)
    valence = emotion_repr.get("valence", 0.0)
    energy = emotion_repr.get("energy", 0.5)
    arousal = emotion_repr.get("arousal", 0.5)
    profile = emotion_repr.get("profile", {})
    reasoning = emotion_repr.get("reasoning", "")
    mode = emotion_repr.get("mode", "baseline")

    st.markdown("### 🧠 Multimodal Emotion Intelligence")
    if reasoning:
        st.info(f"**AI Reasoning:** {reasoning}")

    # Metrics row
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.markdown(
            f"""
            <div class="mm-metric-card">
                <div class="mm-metric-value">{profile.get('emoji', '😐')} {prim.upper()}</div>
                <div class="mm-metric-label">Primary Emotion</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="mm-metric-card">
                <div class="mm-metric-value">{int(conf * 100)}%</div>
                <div class="mm-metric-label">Confidence</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="mm-metric-card">
                <div class="mm-metric-value">{int(intensity * 100)}%</div>
                <div class="mm-metric-label">Intensity</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="mm-metric-card">
                <div class="mm-metric-value">{valence:+.2f}</div>
                <div class="mm-metric-label">Valence</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m5:
        st.markdown(
            f"""
            <div class="mm-metric-card">
                <div class="mm-metric-value">{energy:.2f}</div>
                <div class="mm-metric-label">Energy</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m6:
        st.markdown(
            f"""
            <div class="mm-metric-card">
                <div class="mm-metric-value">{arousal:.2f}</div>
                <div class="mm-metric-label">Arousal</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Visualizer row
    c_rad, c_circ = st.columns(2)
    with c_rad:
        st.markdown("**Emotion Distribution (7-State Affect Radar)**")
        dist = emotion_repr.get("distribution", {})
        if dist:
            st.plotly_chart(create_radar_chart(dist), use_container_width=True)
    with c_circ:
        st.markdown("**Russell Circumplex 2D Coordinates (Valence × Energy)**")
        st.plotly_chart(create_circumplex_plot(valence, energy, prim.capitalize()), use_container_width=True)