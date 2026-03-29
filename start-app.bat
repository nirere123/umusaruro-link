@echo off
REM ============================================
REM Start MySQL and Flask - umusaruro-link
REM ============================================

echo.
echo ==========================================
echo Stopping any existing MySQL processes...
echo ==========================================
taskkill /F /IM mysqld.exe /T 2>nul
timeout /t 3 /nobreak

echo.
echo ==========================================
echo Starting XAMPP MySQL...
echo ==========================================
start "" "C:\xampp\mysql\bin\mysqld.exe"
timeout /t 8 /nobreak

echo.
echo ==========================================
echo Testing MySQL connection...
echo ==========================================
mysql -u root -e "SELECT 1" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ MySQL is running
) else (
    echo ✗ MySQL may not have started properly
)

echo.
echo ==========================================
echo Starting Flask application...
echo ==========================================
cd /d "C:\Users\admin\Desktop\umusaruro-link"
python -m APIs.app

pause
