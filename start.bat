@echo off
echo ============================================
echo Starting AI Surveillance System
echo ============================================
echo.

echo Starting Flask API Server...
start cmd /k "cd backend && python api_server.py"

timeout /t 3 /nobreak > nul

echo Starting React Frontend...
cd frontend
start cmd /k "npm start"

echo.
echo ============================================
echo Application Starting...
echo ============================================
echo Backend API: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul
