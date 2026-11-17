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

:: Ensure port 8501 is free from any previous session
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>nul

:: Start Streamlit server (Streamlit automatically opens the browser once ready)
venv\Scripts\python.exe -m streamlit run ml\app.py --server.port 8501

pause
