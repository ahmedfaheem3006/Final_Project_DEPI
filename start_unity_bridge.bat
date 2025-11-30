@echo off
title Unity Bridge Server
echo Starting Unity Bridge Server...
echo.
echo Installing dependencies...
call npm install socket.io
echo.
echo Starting Server...
node unity_bridge.js
pause
