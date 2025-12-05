@echo off
REM REMZA019 Gaming Desktop - Windows Installation Helper
REM Copyright 2025 019Solutions

title REMZA019 Gaming Desktop Installer
color 0A

echo.
echo ================================================
echo   REMZA019 Gaming Desktop - Windows Installer
echo ================================================
echo.
echo   Professional Gaming Platform by 019Solutions
echo.
echo ================================================
echo.

REM Check for installer file
if not exist "REMZA019-Gaming-Setup-*.exe" (
    echo [ERROR] Installer not found!
    echo.
    echo Please download REMZA019-Gaming-Setup-1.0.0.exe
    echo and place it in the same folder as this script.
    echo.
    pause
    exit /b 1
)

echo [INFO] Installer found
echo.

REM Find the installer
for %%f in (REMZA019-Gaming-Setup-*.exe) do set INSTALLER=%%f

echo [INFO] Running: %INSTALLER%
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
) else (
    echo [WARNING] Not running as Administrator
    echo Some installation features may require elevation
    echo.
)

echo Starting installation...
echo.
echo ================================================
echo.

REM Run the installer
start "" "%INSTALLER%"

if %errorLevel% == 0 (
    echo.
    echo [SUCCESS] Installer launched successfully!
    echo.
    echo Follow the installation wizard to complete setup.
    echo.
    echo After installation:
    echo   - Find shortcut on Desktop
    echo   - Or search "REMZA019 Gaming" in Start Menu
    echo.
) else (
    echo.
    echo [ERROR] Failed to launch installer
    echo Error code: %errorLevel%
    echo.
)

echo ================================================
echo.
echo REMZA019 Gaming Desktop
echo Powered by 019Solutions
echo https://019solutions.com
echo.
echo ================================================
echo.
pause
