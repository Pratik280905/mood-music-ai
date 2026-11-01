"""
Safe External Browser Launcher preferring Google Chrome on Windows.
"""

import os
import subprocess
import webbrowser
from pathlib import Path
from utils.validators import is_safe_url
from utils.logging_config import logger

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
]

def get_chrome_executable() -> Optional[str]:
    """Finds the Google Chrome executable path on the Windows system."""
    for p in CHROME_PATHS:
        if p and os.path.exists(p):
            return p
    return None

def open_url_in_browser(url: str) -> bool:
    """
    Safely opens a validated URL in Google Chrome if available,
    falling back gracefully to the default system browser.
    """
    if not is_safe_url(url):
        logger.warning(f"Rejected non-Spotify or insecure URL: {url}")
        return False

    chrome_exe = get_chrome_executable()
    if chrome_exe:
        try:
            subprocess.Popen([chrome_exe, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Launched URL in Google Chrome: {url}")
            return True
        except Exception as e:
            logger.warning(f"Could not launch Chrome process ({e}). Falling back to default browser.")

    try:
        webbrowser.open(url, new=2)
        logger.info(f"Launched URL via system default browser: {url}")
        return True
    except Exception as e:
        logger.error(f"Failed to open URL in browser: {e}")
        return False