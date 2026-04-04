@echo off
echo =========================================
echo Starting Kinetic Sentinel UI Server
echo =========================================
echo.
echo Open your browser to: http://127.0.0.1:8080
echo.
python -m http.server 8080 -d frontend
