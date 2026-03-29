# ============================================
# Start MySQL and Flask - umusaruro-link
# ============================================

Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "Stopping any existing MySQL processes..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

Get-Process mysqld -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "Starting XAMPP MySQL..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

Start-Process -FilePath "C:\xampp\mysql\bin\mysqld.exe" -WindowStyle Minimized
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "Testing MySQL connection..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

try {
    $conn = New-Object MySql.Data.MySqlClient.MySqlConnection
    $conn.ConnectionString = "server=localhost;uid=root;pwd=;database=mysql"
    $conn.Open()
    Write-Host "✓ MySQL is running" -ForegroundColor Green
    $conn.Close()
} catch {
    Write-Host "✗ MySQL may not have started: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "Starting Flask application..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "API running on: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\Users\admin\Desktop\umusaruro-link"
python -m APIs.app
