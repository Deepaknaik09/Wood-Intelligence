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

:: Free port 8501 from any stale process and allow socket to fully release
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }; Start-Sleep -Milliseconds 800" 2>nul

:: Launch Streamlit server
venv\Scripts\python.exe -m streamlit run ml\app.py --server.port 8501 --browser.gatherUsageStats false

pause
