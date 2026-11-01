"""
Input validation and security helpers for MoodMuse AI.
"""

import re
from urllib.parse import urlparse

SAFE_DOMAINS = {"open.spotify.com", "accounts.spotify.com"}

def sanitize_text(text: str, max_length: int = 500) -> str:
    """Sanitizes user input string and truncates to safe length."""
    if not text:
        return ""
    # Strip HTML tags and control characters
    cleaned = re.sub(r"<[^>]*?>", "", text)
    cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch in "\n\r\t")
    return cleaned.strip()[:max_length]

def is_safe_url(url: str) -> bool:
    """Validates that a URL is a valid HTTPS link to Spotify."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme != "https":
            return False
        netloc = parsed.netloc.lower().split(":")[0]
        return netloc in SAFE_DOMAINS
    except Exception:
        return False

def clamp(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamps a floating point value between min and max."""
    try:
        return max(min_val, min(max_val, float(val)))
    except (ValueError, TypeError):
        return min_val