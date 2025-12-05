@echo off
title REMZA019 Gaming - ULTRA DEBUG
color 0A

echo.
echo ================================================
echo   REMZA019 Gaming - ULTRA DEBUG MODE
echo ================================================
echo.

rem Obriši stare log-ove
del "REMZA-DEBUG.txt" 2>nul
del "%TEMP%\REMZA-DEBUG.txt" 2>nul

echo Starting app...
echo.
start "" "REMZA019-Gaming.exe"

echo Waiting for log file (checking 3 locations)...
timeout /t 3 /nobreak >nul

:CheckLog
rem Proveri lokacija 1 - Current folder
if exist "REMZA-DEBUG.txt" (
    echo.
    echo [SUCCESS] Log found in current folder!
    timeout /t 2 /nobreak >nul
    start notepad "REMZA-DEBUG.txt"
    goto :End
)

rem Proveri lokacija 2 - TEMP folder
if exist "%TEMP%\REMZA-DEBUG.txt" (
    echo.
    echo [SUCCESS] Log found in TEMP folder!
    timeout /t 2 /nobreak >nul
    start notepad "%TEMP%\REMZA-DEBUG.txt"
    goto :End
)

rem Čekaj još malo
echo Still waiting...
timeout /t 2 /nobreak >nul

rem Pokušaj ponovo
if exist "REMZA-DEBUG.txt" (
    start notepad "REMZA-DEBUG.txt"
    goto :End
)

if exist "%TEMP%\REMZA-DEBUG.txt" (
    start notepad "%TEMP%\REMZA-DEBUG.txt"
    goto :End
)

echo.
echo [WARNING] No log file found after 5 seconds!
echo.
echo Checking if app is running...
tasklist | findstr "REMZA019-Gaming.exe" >nul
if %errorlevel%==0 (
    echo App IS running but NO LOG created!
    echo This means logging failed.
) else (
    echo App is NOT running at all!
    echo This means app crashed immediately.
)

echo.
echo Check these locations manually:
echo 1. %CD%\REMZA-DEBUG.txt
echo 2. %TEMP%\REMZA-DEBUG.txt
echo.

:End
pause
