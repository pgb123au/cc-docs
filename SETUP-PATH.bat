@echo off
echo.
echo ============================================
echo   Adding CC to PATH
echo ============================================
echo.
echo This will add C:\Users\peter\Downloads\CC to your User PATH
echo.
pause

powershell -ExecutionPolicy Bypass -File "%~dp0add-to-path.ps1"

pause
