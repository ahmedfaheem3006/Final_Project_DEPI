@echo off
title RG Chatbot - All Servers
echo Starting All Servers...
echo.

start "Chat Server" call start_chat_server.bat
start "TTS Server" call start_tts_server.bat
start "Unity Bridge" call start_unity_bridge.bat

echo All servers started!
echo 1. Chat Server (Port 5000)
echo 2. TTS Server (Port 5001)
echo 3. Unity Bridge (Port 3000)
echo.
pause
