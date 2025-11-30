@echo off
title Coqui TTS Server
echo ========================================
echo   Coqui TTS Server - Free Voice AI
echo ========================================
echo.
echo Installing dependencies...
pip install TTS fastapi uvicorn
echo.
echo Starting TTS Server on port 5001...
echo.
python tts_server.py
pause
