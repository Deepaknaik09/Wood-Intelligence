@echo off
title Wood Intelligence - AI Streamlit App
cd /d "%~dp0"
echo ===================================================
echo  Starting Wood Intelligence AI Streamlit App...
echo  Local URL: http://localhost:8501
echo ===================================================
venv\Scripts\python.exe -m streamlit run ml\app.py
pause

