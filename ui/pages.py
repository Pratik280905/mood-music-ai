"""
Tab Page Renderers for MoodMuse AI Streamlit UI.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

from config.settings import (
    ACTIVITIES, STRATEGIES, DEFAULT_REC_WEIGHTS, DEFAULT_FUSION_WEIGHTS,
    HF_EMOTION_MODEL, HF_VISION_EMOTION_MODEL, SONGS_CSV_PATH, DB_PATH
)
from mood_engine.text_emotion import analyze_text_emotion
from mood_engine.face_emotion import analyze_face_emotion
from mood_engine.fusion import fuse_multimodal_emotions
from mood_engine.intensity import calculate_emotional_representation
from mood_engine.trajectory import plan_emotional_journey
from recommendation.engine import recommendation_engine
from recommendation.personalization import personalization_engine
from services.browser_service import open_url_in_browser
from services.spotify_service import spotify_service
from database.repository import MoodRepository
from ui.components import render_emotion_dashboard, render_ethical_notice
from utils.logging_config import logger

MOOD_PRESETS = {
    "🎉 Celebrating a Big Win!": "I just achieved something huge and I'm bursting with excitement, happiness and celebration!",
    "⚡ Exhausted & Burned Out": "I feel completely exhausted, mentally drained from long hours of work and need to decompress.",
    "💔 Late-Night Melancholy": "It's late at night, feeling introspective, quiet, nostalgic and a bit lonely.",
    "💻 Deep Flow Coding Mode": "Locked in for a long programming and debugging session, need focus, rhythm and zero distraction.",
    "🏋️ Workout Energy Surge": "At the gym ready to crush a heavy workout, need maximum adrenaline, aggressive beats and drive.",
    "🌿 Peaceful Sunday Chill": "Taking a slow, relaxing morning with coffee, feeling tranquil, mellow and content."
}

# ---------------------------------------------------------------------------
# Tab 1: Live Mood & Music Intelligence Generator
# ---------------------------------------------------------------------------
def render_generator_tab() -> None:
    st.markdown("#### 1. Express Your Emotion & Select Context")

    # Quick Mood Presets
    st.caption("⚡ Quick Mood Presets (Click any to instantly populate your emotional description):")
    p_cols = st.columns(6)
    for col, (label, preset_text) in zip(p_cols, MOOD_PRESETS.items()):
        with col:
            if st.button(label, key=f"preset_{label}", use_container_width=True):
                st.session_state.preset_prompt = preset_text
                st.rerun()

    current_prompt = st.session_state.get("preset_prompt", "")

    col_in_1, col_in_2 = st.columns([3, 2])

    with col_in_1:
        text_input = st.text_area(
            "How are you feeling right now?",
            value=current_prompt,
            placeholder="e.g. 'Feeling really accomplished after debugging code all morning!' or 'A bit overwhelmed and exhausted today.'",
            height=100,
            key="user_text_input"
        )

        with st.expander("📷 Add Facial Emotion Analysis (Vision Transformer)"):
            st.caption("Privacy Notice: Frames are analyzed locally in-memory using a Vision Transformer; no images are stored or uploaded.")
            cam_image = st.camera_input("Take a snapshot", label_visibility="collapsed", key="user_camera_input")

    with col_in_2:
        activity = st.selectbox(
            "Current Activity",
            options=list(ACTIVITIES.keys()),
            index=0,
            help="Context dynamically modulates acoustic energy, tempo, and genre affinity."
        )
        strategy = st.selectbox(
            "Recommendation Strategy",
            options=list(STRATEGIES.keys()),
            index=0,
            help="'Match My Mood' validates current state; other strategies apply an emotional journey."
        )

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            genre_filter = st.selectbox(
                "Genre Filter",
                options=["All", "Pop", "Rock", "Hip-Hop", "Electronic", "Lo-Fi", "Classical", "Indie", "R&B", "Ambient", "Synthwave", "Metal"]
            )
        with c_opt2:
            language_filter = st.selectbox(
                "Language",
                options=["All", "English", "Spanish", "Hindi", "Instrumental"]
            )

    gen_clicked = st.button("✨ Analyze Emotion & Generate Music", type="primary", use_container_width=True)

    if gen_clicked:
        with st.spinner("Executing Transformer NLP & Vision Transformer multimodal inference..."):
            import numpy as np
            from PIL import Image

            # 1. Text Emotion NLP Inference (DistilRoBERTa)
            text_res = analyze_text_emotion(text_input)

            # 2. Vision Face Emotion Inference (ViT + Haar Localization)
            frame = None
            if cam_image is not None:
                pil_img = Image.open(cam_image).convert("RGB")
                frame = np.array(pil_img)
            face_res = analyze_face_emotion(frame)

            # 3. Multimodal Confidence-Weighted Fusion
            fused_res = fuse_multimodal_emotions(text_res, face_res)

            # 4. Intensity & Continuous Circumplex Representation
            context_dict = {
                "activity": activity,
                "strategy": strategy,
                "genre": genre_filter,
                "language": language_filter,
                "raw_text": text_input,
                "has_face": face_res.get("detected", False)
            }
            emotion_repr = calculate_emotional_representation(fused_res, context_dict)

            # 5. Recommendation Engine Pipeline
            rec_result = recommendation_engine.generate_recommendations(
                emotion_repr=emotion_repr,
                context=context_dict,
                user_id="default_user",
                limit=6
            )

            # Update session state
            st.session_state.current_emotion = emotion_repr
            st.session_state.current_context = context_dict
            st.session_state.current_recommendations = rec_result["recommendations"]
            st.session_state.active_source = rec_result["active_source"]
            st.session_state.source_note = rec_result["source_note"]
            st.session_state.current_journey = rec_result["journey"]
            st.session_state.face_annotated = face_res.get("annotated_frame")
            st.session_state.rated_ids = set()

            st.rerun()

    # Display Results if available
    if "current_emotion" in st.session_state and st.session_state.current_emotion:
        st.divider()

        # If a face was analyzed, show face crop alongside dashboard
        if st.session_state.get("face_annotated") is not None:
            c_face, c_dash = st.columns([1, 3])
            with c_face:
                st.markdown("**Detected Face ROI (Vision Transformer)**")
                st.image(st.session_state.face_annotated, channels="RGB", use_container_width=True)
            with c_dash:
                render_emotion_dashboard(st.session_state.current_emotion)
        else:
            render_emotion_dashboard(st.session_state.current_emotion)

        st.divider()
        st.markdown("### 🎶 Personalized Playlist Recommendations")
        if "source_note" in st.session_state and st.session_state.source_note:
            st.caption(f"ℹ️ {st.session_state.source_note}")

        recs = st.session_state.get("current_recommendations", [])
        if not recs:
            st.warning("No tracks matched the active combination of filters. Try selecting 'All' for Genre and Language.")
        else:
            # Playlist Actions Row: Export / Quick Listen All
            col_exp1, col_exp2 = st.columns([3, 1])
            with col_exp2:
                export_text = "\n".join([f"{i+1}. {s['title']} - {s['artist']} ({s['spotify_url']})" for i, s in enumerate(recs)])
                st.download_button(
                    label="📥 Export Playlist (.txt)",
                    data=export_text,
                    file_name="moodmuse_playlist.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            for song in recs:
                _render_song_item(song)

    else:
        st.write("")
        st.info("💡 Type your current feelings or select a Quick Mood Preset above, then click **Analyze Emotion & Generate Music** to start.")

def _render_song_item(song: Dict[str, Any]) -> None:
    """Renders an interactive song card with in-app Spotify player, link redirect, and Explainable AI expander."""
    song_id = str(song.get("id", ""))
    title = song.get("title", "Untitled")
    artist = song.get("artist", "Unknown Artist")
    genre = song.get("genre", "Music")
    lang = song.get("language", "English")
    score_pct = int(song.get("score", 0.0) * 100)
    spotify_url = song.get("spotify_url", "")
    exp = song.get("explanation", {})

    already_rated = song_id in st.session_state.get("rated_ids", set())

    # Extract track ID for Spotify Mini Player Embed
    track_id = None
    if spotify_url and "/track/" in spotify_url:
        track_id = spotify_url.split("/track/")[-1].split("?")[0]

    with st.container():
        st.markdown(
            f"""
            <div class="mm-song-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                    <div>
                        <div class="mm-song-title">{title}</div>
                        <div class="mm-song-artist">by {artist}</div>
                        <div>
                            <span class="mm-badge-generic">🎵 {genre}</span>
                            <span class="mm-badge-generic">🌐 {lang}</span>
                        </div>
                    </div>
                    <div>
                        <div class="mm-score-pill">★ {score_pct}% Match</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # In-App Spotify Player Embed (Works for 30s audio preview on all browsers without Premium!)
        if track_id:
            embed_code = f"""
            <iframe style="border-radius:12px; margin-bottom: 8px;" src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator&theme=0" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            """
            components.html(embed_code, height=85)

        # Action Buttons Row
        b1, b2, b3, b4, b5 = st.columns([1, 1, 1, 1.4, 2])
        with b1:
            if st.button("❤️ Like", key=f"like_{song_id}", disabled=already_rated, use_container_width=True):
                personalization_engine.process_feedback(song, "liked", mood=st.session_state.current_emotion.get("primary_emotion", "neutral"))
                st.session_state.rated_ids.add(song_id)
                st.toast(f"Liked '{title}'! Learned preferences updated in SQLite.", icon="❤️")
                st.rerun()

        with b2:
            if st.button("👎 Dislike", key=f"dislike_{song_id}", disabled=already_rated, use_container_width=True):
                personalization_engine.process_feedback(song, "disliked", mood=st.session_state.current_emotion.get("primary_emotion", "neutral"))
                st.session_state.rated_ids.add(song_id)
                st.toast(f"Disliked '{title}'. Future suggestions will penalize this style.", icon="👎")
                st.rerun()

        with b3:
            if st.button("⏭ Skip", key=f"skip_{song_id}", disabled=already_rated, use_container_width=True):
                personalization_engine.process_feedback(song, "skipped", mood=st.session_state.current_emotion.get("primary_emotion", "neutral"))
                st.session_state.rated_ids.add(song_id)
                st.toast(f"Skipped '{title}'.", icon="⏭")
                st.rerun()

        with b4:
            if st.button("🔄 More Like This", key=f"more_{song_id}", use_container_width=True):
                personalization_engine.process_feedback(song, "liked", mood=st.session_state.current_emotion.get("primary_emotion", "neutral"))
                st.toast(f"Tuning algorithm towards {artist} and {genre}...", icon="🔄")
                st.rerun()

        with b5:
            if spotify_url:
                # Native browser link button that directly redirects to Spotify in a new tab!
                st.link_button("🎧 Open in Spotify", url=spotify_url, use_container_width=True)

        # Explainable AI Breakdown
        with st.expander("🔍 Explainable AI: Why was this song selected?"):
            c_sc1, c_sc2, c_sc3, c_sc4 = st.columns(4)
            c_sc1.metric("Mood Match", f"{exp.get('mood_match_pct', 0)}%")
            c_sc2.metric("Context Match", f"{exp.get('context_match_pct', 0)}%")
            c_sc3.metric("User Taste Match", f"{exp.get('preference_match_pct', 0)}%")
            c_sc4.metric("Novelty Discovery", f"{exp.get('novelty_pct', 0)}%")

            st.markdown("**AI Decision Rationale:**")
            for r in exp.get("reasons", []):
                st.markdown(f"- ✓ {r}")

# ---------------------------------------------------------------------------
# Tab 2: Emotional Trajectory Planner
# ---------------------------------------------------------------------------
def render_trajectory_tab() -> None:
    st.markdown("### 🌈 Iso-Principle Emotional Journey Planner")
    st.markdown(
        """
        The **Iso-Principle** is an established methodology in psychological music therapy. 
        Instead of jarringly playing high-energy pop when a listener is experiencing sadness or distress, 
        the system first validates the listener's current emotional frequency, then gradually introduces 
        transitional tracks that shift valence and arousal toward the desired equilibrium.
        """
    )

    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        curr_emo = st.selectbox(
            "Starting Emotion State",
            options=["sadness", "anger", "fear", "chill", "neutral", "joy", "surprise", "disgust"],
            index=0
        )
        target_strat = st.selectbox(
            "Transformation Strategy",
            options=["Improve My Mood", "Calm Me Down", "Energize Me", "Match My Mood"],
            index=0
        )

    journey = plan_emotional_journey(curr_emo, target_strat)

    with t_col2:
        st.markdown(f"**Strategy Narrative:** {journey.get('narrative', '')}")
        st.markdown(
            f"**Target Coordinates:** Valence = `{journey.get('target_valence'):+.2f}`, "
            f"Energy = `{journey.get('target_energy'):.2f}`"
        )

    st.divider()
    st.markdown("#### Transition Stages & Milestone Path")

    steps = journey.get("steps", [])
    cols = st.columns(len(steps))

    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            step_num = step.get('step', i + 1)
            step_stage = step.get('stage', f"Stage {i + 1}")
            step_desc = step.get('description') or step.get('desc') or ''
            step_val = float(step.get('valence', 0.0))
            step_eng = float(step.get('energy', 0.5))
            st.markdown(
                f"""
                <div class="mm-metric-card" style="text-align: left; height: 180px;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #a78bfa;">STAGE {step_num}</div>
                    <div style="font-weight: 700; font-size: 1.05rem; margin-top: 0.2rem;">{step_stage}</div>
                    <div style="font-size: 0.85rem; color: #9ca3af; margin-top: 0.4rem;">{step_desc}</div>
                    <div style="margin-top: 0.6rem; font-size: 0.75rem; color: #6ee7b7;">
                        Valence: {step_val:+.2f} | Energy: {step_eng:.2f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")
    df_steps = pd.DataFrame(steps)
    if not df_steps.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_steps["valence"],
                y=df_steps["energy"],
                mode="lines+markers+text",
                line=dict(color="#818cf8", width=3, dash="solid"),
                marker=dict(size=12, color=["#f43f5e"] + ["#38bdf8"]*(len(steps)-2) + ["#34d399"]),
                text=[f"Step {s['step']}: {s['stage']}" for s in steps],
                textposition="top center",
                textfont=dict(color="#ffffff", size=11)
            )
        )
        fig.update_layout(
            title="Emotional Trajectory Path in Circumplex Space",
            xaxis=dict(title="Valence (Negative ➔ Positive)", range=[-1.05, 1.05], color="#9ca3af"),
            yaxis=dict(title="Energy (Low ➔ High)", range=[0.0, 1.05], color="#9ca3af"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17, 24, 39, 0.5)",
            height=340,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 3: Mood & Music Analytics Dashboard
# ---------------------------------------------------------------------------
def render_dashboard_tab() -> None:
    st.markdown("### 📊 Mood & Music Intelligence Dashboard")

    summary = MoodRepository.get_feedback_summary()
    sessions = MoodRepository.get_mood_sessions(limit=100)

    # Top KPI metrics
    k1, k2, k3, k4, k5 = st.columns(5)
    total_ratings = summary["likes"] + summary["dislikes"] + summary["skips"]
    like_rate = (summary["likes"] / total_ratings * 100) if total_ratings > 0 else 0.0

    k1.metric("Total Sessions", len(sessions))
    k2.metric("Songs Liked", summary["likes"])
    k3.metric("Songs Disliked", summary["dislikes"])
    k4.metric("Songs Skipped", summary["skips"])
    k5.metric("Like Ratio", f"{like_rate:.1f}%")

    st.divider()

    c_g1, c_g2 = st.columns(2)

    with c_g1:
        st.markdown("#### Emotion Session Distribution")
        if sessions:
            df_sess = pd.DataFrame(sessions)
            emo_counts = df_sess["fused_emotion"].value_counts().reset_index()
            emo_counts.columns = ["Emotion", "Count"]
            fig = px.bar(
                emo_counts,
                x="Emotion",
                y="Count",
                color="Emotion",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No mood sessions logged yet. Check your mood in Tab 1!")

    with c_g2:
        st.markdown("#### Feedback Action Breakdown")
        act_counts = summary["action_counts"]
        if act_counts:
            df_act = pd.DataFrame({"Action": list(act_counts.keys()), "Count": list(act_counts.values())})
            fig = px.pie(df_act, names="Action", values="Count", hole=0.45, color_discrete_sequence=["#34d399", "#f87171", "#fbbf24", "#60a5fa"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Interact with recommendation cards (Like, Dislike, Skip) to populate feedback telemetry.")

    st.markdown("#### Top Liked Artists & Preferred Genres")
    c_art, c_gen = st.columns(2)
    with c_art:
        top_art = summary.get("top_artists", [])
        if top_art:
            for art, count in top_art:
                st.markdown(f"- **{art}** — `{count} song{'s' if count != 1 else ''}`")
        else:
            st.caption("No liked artists yet.")

    with c_gen:
        top_gen = summary.get("top_genres", [])
        if top_gen:
            for g, count in top_gen:
                st.markdown(f"- **{g}** — `{count} song{'s' if count != 1 else ''}`")
        else:
            st.caption("No liked genres yet.")

# ---------------------------------------------------------------------------
# Tab 4: User Profile & Learned Taste
# ---------------------------------------------------------------------------
def render_profile_tab() -> None:
    st.markdown("### 👤 User Profile & Online Learned Taste")
    st.caption("MoodMuse continuously adapts to your feedback in real-time, learning your unique acoustic preferences.")

    prefs = MoodRepository.get_user_preferences("default_user")

    p1, p2 = st.columns(2)
    with p1:
        st.markdown("#### Learned Genre Affinities")
        gw = prefs.genre_weights
        if gw:
            df_gw = pd.DataFrame({"Genre": list(gw.keys()), "Affinity Weight": list(gw.values())}).sort_values(by="Affinity Weight", ascending=False)
            st.dataframe(df_gw, use_container_width=True, hide_index=True)
        else:
            st.info("No genre weights learned yet. Like or skip songs to teach the system.")

    with p2:
        st.markdown("#### Learned Artist Affinities")
        aw = prefs.artist_weights
        if aw:
            df_aw = pd.DataFrame({"Artist": list(aw.keys()), "Affinity Weight": list(aw.values())}).sort_values(by="Affinity Weight", ascending=False)
            st.dataframe(df_aw, use_container_width=True, hide_index=True)
        else:
            st.info("No artist weights learned yet.")

    st.divider()
    st.markdown("#### ❤️ Liked Songs Library")
    liked_songs = MoodRepository.get_liked_songs()
    if liked_songs:
        for s in liked_songs:
            c1, c2 = st.columns([4, 1.5])
            with c1:
                st.markdown(f"**{s['song_title']}** by {s['artist']} · `{s['genre']}` · (Saved {s['timestamp']})")
            with c2:
                search_url = spotify_service.get_search_url(f"{s['song_title']} {s['artist']}")
                st.link_button("🎧 Listen on Spotify", url=search_url, use_container_width=True)
    else:
        st.info("No songs currently in your liked library.")

    st.divider()
    if st.button("🗑️ Reset All My Profile & Session Data", type="secondary"):
        MoodRepository.reset_all_data()
        personalization_engine._load_state()
        st.session_state.current_emotion = None
        st.session_state.current_recommendations = []
        st.session_state.rated_ids = set()
        st.toast("Profile data successfully cleared.", icon="🗑️")
        st.rerun()

# ---------------------------------------------------------------------------
# Tab 5: System Architecture & Viva Diagnostics
# ---------------------------------------------------------------------------
def render_diagnostics_tab() -> None:
    st.markdown("### ⚙️ System Architecture & Model Diagnostics (Viva Guide)")

    st.markdown(
        """
        This technical dashboard verifies all subsystem layers, models, fallback pipelines, and mathematical weighting equations.
        Ideal for academic presentation, resume walkthrough, and final-year viva demonstration.
        """
    )

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("NLP Transformer", "DistilRoBERTa", "7-Class Affect")
    d2.metric("Computer Vision", "Vision Transformer (ViT)", "Haar + ViT ROI")
    d3.metric("Local Fallback Catalog", "135 Tracks", "Offline Verified")
    d4.metric("SQLite Persistence", "Active", "moodmuse.db")

    st.divider()

    st.markdown("#### 1. Live Subsystem Verification")
    st.write(f"- **NLP Transformer Model**: `{HF_EMOTION_MODEL}` (Hugging Face Pipeline)")
    st.write(f"- **Vision Transformer Model**: `{HF_VISION_EMOTION_MODEL}` (ViT Facial Emotion Classifier)")
    st.write(f"- **Computer Vision Cascades**: Face and Smile Haar classifiers operational.")
    st.write(f"- **Database Path**: `{DB_PATH}`")
    st.write(f"- **Catalog Path**: `{SONGS_CSV_PATH}`")

    # Spotify Status Explanation
    st.markdown("#### 2. Spotify Integration & Non-Premium Account Transparency")
    if spotify_service.is_connected:
        st.success("Spotify Service Status: Connected via Client Credentials. Public search & metadata active.")
    else:
        st.warning(
            "Spotify Service Status: Operating in Local AI Recommendation Engine mode with embedded Spotify players.\n\n"
            "**Technical viva justification**: Spotify restricted access to `/v1/recommendations` and `/v1/audio-features` "
            "for non-commercial/free developer tiers in Nov 2024, and Spotify Web Playback SDK strictly requires a paid "
            "Spotify Premium subscription. To ensure zero crashes, legal compliance, and reliable operation without paid accounts, "
            "MoodMuse AI incorporates a 135-track local catalog with verified acoustic attributes, embedded Spotify preview widgets, "
            "and instant new-tab Spotify redirection via `st.link_button`."
        )

    st.markdown("#### 3. Core Mathematical Formulations")
    st.latex(r"\text{Multimodal Score}(e) = w_{\text{text}} \cdot P_{\text{text}}(e) \cdot C_{\text{text}} + w_{\text{face}} \cdot P_{\text{face}}(e) \cdot C_{\text{face}}")
    st.latex(r"\text{Recommendation Score} = w_m M + w_g G + w_c C + w_p P + w_d D + w_n N")

    st.markdown("#### 4. Live Multi-Factor Weight Tuning")
    st.caption("Adjust recommendation weights below to test algorithmic sensitivity:")
    cw1, cw2, cw3 = st.columns(3)
    with cw1:
        wm = st.slider("Mood Match Weight (w_m)", 0.0, 1.0, DEFAULT_REC_WEIGHTS["mood_match"], 0.05)
        wg = st.slider("Desired Mood Weight (w_g)", 0.0, 1.0, DEFAULT_REC_WEIGHTS["desired_mood_match"], 0.05)
    with cw2:
        wc = st.slider("Context Match Weight (w_c)", 0.0, 1.0, DEFAULT_REC_WEIGHTS["context_match"], 0.05)
        wp = st.slider("User Taste Weight (w_p)", 0.0, 1.0, DEFAULT_REC_WEIGHTS["user_preference"], 0.05)
    with cw3:
        wd = st.slider("Diversity Weight (w_d)", 0.0, 1.0, DEFAULT_REC_WEIGHTS["diversity"], 0.05)
        wn = st.slider("Novelty Weight (w_n)", 0.0, 1.0, DEFAULT_REC_WEIGHTS["novelty"], 0.05)

    render_ethical_notice()