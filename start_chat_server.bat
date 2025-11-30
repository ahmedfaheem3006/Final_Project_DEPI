@echo off
title Chat Bot Server
echo Starting Chat Bot Server...
echo.
echo Installing requirements...
pip install flask flask-cors google-generativeai python-dotenv
echo.
echo Starting Server...
python server.py
pause
