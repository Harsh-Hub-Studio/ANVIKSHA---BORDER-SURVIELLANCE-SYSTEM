@echo off
title Border Surveillance Command Center Launcher
echo Starting the AI-Based Border Infiltration System...

:: Step 1: Start the Python AI Video Stream (api.py)
:: This opens a new command prompt, activates the virtual environment, and runs the API
echo Launching Python AI Video API...
start "AI Video API (Port 5001)" cmd /k "call venv\Scripts\activate && python api.py"

:: Step 2: Start the Node.js MQTT Bridge (server.js)
:: Assumes server.js is in the same main folder. If it's in a subfolder, add a cd command first.
echo Launching Node.js Alert Backend...
start "Node.js Alert Bridge (Port 5000)" cmd /k "node server.js"

:: Step 3: Start the React TSX Dashboard
:: Assumes your React app is in a folder called 'frontend'. Change if named differently!
echo Launching React Dashboard...
start "React Command Center (Port 3000)" cmd /k "cd frontend && npm start"

echo All systems initialized! Close this window whenever you are ready.
pause