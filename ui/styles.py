"""
Modern Dark Glassmorphism CSS Styles for MoodMuse AI Streamlit UI.
"""

def get_custom_css() -> str:
    return """
    <style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #0b0f19 0%, #111827 50%, #070a11 100%);
        color: #f3f4f6;
    }

    /* Hero Banner */
    .mm-hero-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .mm-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .mm-tagline {
        font-size: 1.05rem;
        color: #9ca3af;
        font-weight: 400;
        margin-bottom: 0.8rem;
    }

    /* Badges */
    .mm-source-badge-spotify {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #4ade80;
        margin-right: 0.5rem;
    }

    .mm-source-badge-fallback {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        background: rgba(234, 179, 8, 0.15);
        border: 1px solid rgba(234, 179, 8, 0.35);
        color: #facc15;
        margin-right: 0.5rem;
    }

    .mm-badge-generic {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #e5e7eb;
        margin-right: 0.4rem;
    }

    /* Song Card */
    .mm-song-card {
        background: rgba(31, 41, 55, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .mm-song-card:hover {
        border-color: rgba(167, 139, 250, 0.4);
        transform: translateY(-2px);
    }

    .mm-song-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f9fafb;
        margin-bottom: 0.1rem;
    }

    .mm-song-artist {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
    }

    .mm-score-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.4);
        font-size: 0.9rem;
        font-weight: 700;
        color: #818cf8;
    }

    /* Emotion Metrics Card */
    .mm-metric-card {
        background: rgba(31, 41, 55, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        text-align: center;
    }

    .mm-metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f9fafb;
    }

    .mm-metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
        margin-top: 0.2rem;
    }

    /* Notice Banner */
    .mm-notice-banner {
        background: rgba(30, 58, 138, 0.25);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        font-size: 0.85rem;
        color: #bfdbfe;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }

    button[kind="secondary"] {
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    </style>
    """