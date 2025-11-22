@echo off
echo Starting to package Clipboard Helper...
echo.

REM Clean previous build files
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "*.spec" del /q "*.spec"

echo [1/3] Cleaned old files
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found, installing...
    python -m pip install pyinstaller
    echo.
)

echo [2/3] Building executable...
echo.

REM Build command
pyinstaller --name=ClipboardHelper --onefile --windowed main.py

echo.
echo [3/3] Checking result...
echo.

if exist "dist\ClipboardHelper.exe" (
    echo ========================================
    echo    Build Successful!
    echo ========================================
    echo.
    echo Executable: dist\ClipboardHelper.exe
    echo.
    echo Hotkeys:
    echo   Ctrl+Space: Batch paste
    echo   Ctrl+Shift+C: Show/Hide window
    echo   Ctrl+Shift+Q: Quit
    echo.
) else (
    echo ========================================
    echo    Build Failed!
    echo ========================================
    echo Please check the error messages above
    echo.
)

pause
