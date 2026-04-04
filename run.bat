@echo off
echo =========================================
echo Starting Kinetic Sentinel FastAPI Server
echo =========================================
echo.
.\venv\Scripts\uvicorn.exe main:app --reload
