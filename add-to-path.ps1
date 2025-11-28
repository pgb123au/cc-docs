# PowerShell script to add CC directory to User PATH
# Run this as: powershell -ExecutionPolicy Bypass -File add-to-path.ps1

$ccPath = "C:\Users\peter\Downloads\CC"

Write-Host "Adding $ccPath to User PATH..." -ForegroundColor Cyan

# Get current User PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check if already in PATH
if ($currentPath -like "*$ccPath*") {
    Write-Host "Directory is already in PATH!" -ForegroundColor Yellow
    Write-Host "Current User PATH: $currentPath" -ForegroundColor Gray
} else {
    # Add to PATH
    $newPath = $currentPath + ";" + $ccPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

    Write-Host "Successfully added to PATH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: You must restart your terminal/command prompt for changes to take effect!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After restarting, you can type 'run' from any directory." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host
