@echo off
echo ================================
echo AI Surveillance Camera System
echo Installation Script
echo ================================
echo.

echo Installing required packages...
pip install opencv-python numpy insightface onnxruntime Pillow

echo.
echo ================================
echo Installation complete!
echo ================================
echo.
echo Next steps:
echo 1. Run: python test_setup.py   (to verify installation)
echo 2. Run: python main.py         (command-line mode)
echo 3. Run: python gui.py          (GUI dashboard)
echo.
pause
