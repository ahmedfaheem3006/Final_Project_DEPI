@echo off
title Interior Design Server
echo Starting Interior Design Server...
echo.
cd "Interior-Design-Video-Generator-main"
echo Installing requirements (if missing)...
pip install -r requirements.txt
echo.
echo Starting Server...
python InteriorDesignGenerator.py
pause
