@echo off
echo ========================================
echo  Building YouTube2Audio
echo ========================================
echo.

:: Activate venv
call venv\Scripts\activate.bat

:: Install build dependencies
echo [1/4] Installing dependencies...
pip install pyinstaller Pillow --quiet

:: Build exe
echo [2/4] Building executable...
pyinstaller --onefile --windowed --icon=music.ico --name=YouTube2Audio --add-data="music.ico;." main.py

:: Cleanup
echo [4/4] Cleaning up...
if exist build rmdir /s /q build
if exist YouTube2Audio.spec del YouTube2Audio.spec

echo.
echo ========================================
if exist dist\YouTube2Audio.exe (
    echo  Build successful!
    echo  Output: dist\YouTube2Audio.exe
) else (
    echo  Build failed! Check errors above.
)
echo ========================================
pause
