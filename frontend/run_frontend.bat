@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting Job AI Frontend
echo ========================================
echo.

set "NODEJS_PATH=C:\Program Files\nodejs-portable\node-v20.11.0-win-x64"
set "PATH=%NODEJS_PATH%;%PATH%"

cd /d "d:\Main project\Job AI_2\frontend"

echo Checking Node.js...
"%NODEJS_PATH%\node.exe" --version
if errorlevel 1 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)

echo.
echo Checking npm...
"%NODEJS_PATH%\npm.cmd" --version
if errorlevel 1 (
    echo ERROR: npm not found!
    pause
    exit /b 1
)

echo.
echo Starting Next.js development server...
echo.
"%NODEJS_PATH%\npm.cmd" run dev

pause
