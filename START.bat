@echo off
REM ================================================
REM 🌊 WATER QUALITY PREDICTION API - ONE-CLICK RUN
REM ================================================
REM This batch file starts everything automatically
REM ================================================

echo.
echo ================================================
echo    Water Quality Prediction API
echo    Launching in 3 seconds...
echo ================================================
echo.

timeout /t 2 /nobreak

cd /d "%~dp0"
python run.py

pause
