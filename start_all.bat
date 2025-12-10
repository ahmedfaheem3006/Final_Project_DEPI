@echo off
title RG Chatbot - All Servers
echo Starting All Servers...
echo.

start "Chat Server" start_chat_server.bat
rem start "TTS Server" start_tts_server.bat
start "Unity Bridge" start_unity_bridge.bat

echo All servers started!
echo 1. Chat Server (Port 5000)
echo 2. Unity Bridge (Port 3000)
echo.
pause
