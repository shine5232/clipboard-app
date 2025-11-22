@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Clipboard Helper - Build Script
echo ========================================
echo.

:: Step 1: Check Python
echo [Step 1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python first.
    pause
    exit /b 1
)
python --version
echo.

:: Step 2: Install/Check PyInstaller
echo [Step 2/5] Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)
echo PyInstaller is ready
echo.

:: Step 3: Clean old files
echo [Step 3/5] Cleaning old build files...
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q "dist"
)
if exist "build" (
    echo Removing build folder...
    rmdir /s /q "build"
)
if exist "*.spec" (
    echo Removing spec files...
    del /q "*.spec"
)
echo Clean complete
echo.

:: Step 4: Build
echo [Step 4/5] Building executable...
echo This may take 1-2 minutes...
echo.

pyinstaller ^
    --name=ClipboardHelper ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.

:: Step 5: Verify
echo [Step 5/5] Verifying build...
if exist "dist\ClipboardHelper.exe" (
    echo.
    echo ========================================
    echo         BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Output: dist\ClipboardHelper.exe

    :: Get file size
    for %%A in ("dist\ClipboardHelper.exe") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo Size: !sizeMB! MB
    )

    echo.
    echo Usage:
    echo 1. Copy ClipboardHelper.exe to any location
    echo 2. Double-click to run
    echo.
    echo Hotkeys:
    echo   Ctrl+Space       : Batch paste
    echo   Ctrl+Shift+C     : Show/Hide window
    echo   Ctrl+Shift+Q     : Quit
    echo.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo         BUILD FAILED!
    echo ========================================
    echo.
    echo The executable was not created.
    echo Please check the error messages above.
    echo.
)

pause
