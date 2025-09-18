@echo off
echo Starting TalentFitAI Backend Server...
echo ================================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    echo Make sure you're in the correct directory and venv exists
    pause
    exit /b 1
)

REM Start the server
python start_server.py

pause
