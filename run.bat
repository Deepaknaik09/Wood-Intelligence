@echo off
title Wood Intelligence — AI Timber Atelier
cd /d "%~dp0"

echo ===============================================================
echo          WOOD INTELLIGENCE - AI TIMBER ATELIER
echo ===============================================================
echo  Starting Application: http://localhost:8501
echo  (Species Identification, Defect Detection, Furniture Studio)
echo ===============================================================
echo.

:: Automatically open browser directly to localhost:8501
start http://localhost:8501

:: Start Streamlit server
venv\Scripts\python.exe -m streamlit run ml\app.py --server.port 8501

pause
