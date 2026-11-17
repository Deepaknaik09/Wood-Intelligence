@echo off
title Wood Intelligence - Industrial Timber Inspection
cd /d "%~dp0"

echo ===============================================================
echo       WOOD INTELLIGENCE - INDUSTRIAL TIMBER INSPECTION
echo ===============================================================
echo  Application Endpoint: http://localhost:8501
echo  (Species Classification, Defect Segmentation, Joinery Studio)
echo ===============================================================
echo.

:: Automatically open browser directly to localhost:8501
start http://localhost:8501

:: Start Streamlit server
venv\Scripts\python.exe -m streamlit run ml\app.py --server.port 8501

pause
