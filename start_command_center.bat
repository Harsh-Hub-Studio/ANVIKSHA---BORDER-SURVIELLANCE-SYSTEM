@echo off
title Border Surveillance Command Center Launcher
echo Starting the AI-Based Border Infiltration System...

:: Step 1: Start the Python AI Video Stream (main.py)
:: This opens a new command prompt, activates the virtual environment, and runs the main application
echo Launching Python AI Video API...
start "AI Video API (Port 5001)" cmd /k "python main.py"


:: Step 3: Start the React TSX Dashboard
:: Assumes your React app is in a folder called 'frontend'. Change if named differently!
echo Launching React Dashboard...
start "React Command Center (Port 3000)" cmd /k "cd frontend && npm start"

echo All systems initialized! Close this window whenever you are ready.
pause