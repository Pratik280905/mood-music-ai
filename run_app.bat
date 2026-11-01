@echo off
title MoodMuse AI
cd /d "C:\Users\Priyanka\OneDrive\Desktop\mood-music-ai"
echo Starting MoodMuse AI...
call venv\Scripts\activate.bat
streamlit run app.py
pause