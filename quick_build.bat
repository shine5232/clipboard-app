@echo off
echo Building Clipboard Helper...
echo.

:: Clean old files
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Build
pyinstaller --name=ClipboardHelper --onefile --windowed --noconfirm main.py

:: Check result
if exist "dist\ClipboardHelper.exe" (
    echo.
    echo SUCCESS! File: dist\ClipboardHelper.exe
) else (
    echo.
    echo FAILED! Please check errors above.
)

echo.
pause
