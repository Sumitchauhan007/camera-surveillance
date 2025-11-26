@echo off
echo ============================================
echo AI Surveillance System - Complete Setup
echo ============================================
echo.

echo [1/4] Installing Python dependencies...
cd backend
pip install -r ..\requirements.txt
cd ..

echo.
echo [2/4] Testing InsightFace installation...
python -c "from insightface.app import FaceAnalysis; print('✓ InsightFace is ready!')"

echo.
echo [3/4] Installing React dependencies...
cd frontend
call npm install

echo.
echo [4/4] Setup complete!
echo.
echo ============================================
echo To start the application:
echo ============================================
echo.
echo Terminal 1 - Backend API:
echo   cd backend
echo   python api_server.py
echo.
echo Terminal 2 - React Frontend:
echo   cd frontend
echo   npm start
echo.
echo Then open: http://localhost:3000
echo ============================================
pause
