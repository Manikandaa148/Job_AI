@echo off
set "PATH=C:\Program Files\nodejs-portable\node-v20.11.0-win-x64;%PATH%"
cd /d "d:\Main project\Job AI_2\frontend"
echo [INFO] Starting Next.js development server...
echo [INFO] Node path: %PATH%
call npm run dev 2>&1
