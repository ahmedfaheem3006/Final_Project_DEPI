@echo off
title Image Generation Proxy
echo Starting Image Generation Proxy Server...
echo.
echo Installing dependencies...
pip install requests
echo.
python image_proxy_server.py
pause
