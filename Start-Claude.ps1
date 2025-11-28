# Start-Claude.ps1 - Claude CLI Launcher with Folder Selection
# Double-click or run from PowerShell to launch

$Host.UI.RawUI.WindowTitle = "Claude CLI Launcher"

# Define your project folders
$folders = @(
    @{ Name = "CC (Main)";           Path = "C:\Users\peter\Downloads\CC" }
    @{ Name = "RetellAI Agents";     Path = "C:\Users\peter\Downloads\CC\retell" }
    @{ Name = "n8n Workflows";       Path = "C:\Users\peter\Downloads\CC\n8n" }
    @{ Name = "Agents";              Path = "C:\Users\peter\Downloads\CC\agents" }
    @{ Name = "Tools";               Path = "C:\Users\peter\Downloads\CC\tools" }
    @{ Name = "Quick Scripts";       Path = "C:\Users\peter\Downloads\CC\quick-scripts" }
    @{ Name = "Learning";            Path = "C:\Users\peter\Downloads\CC\learning" }
    @{ Name = "Shared";              Path = "C:\Users\peter\Downloads\CC\shared" }
)

# Recent folders file
$recentFile = "$env:USERPROFILE\.claude-recent-folders.txt"

function Get-RecentFolders {
    if (Test-Path $recentFile) {
        return Get-Content $recentFile | Select-Object -First 3
    }
    return @()
}

function Save-RecentFolder {
    param([string]$folder)
    $recent = @($folder)
    if (Test-Path $recentFile) {
        $existing = Get-Content $recentFile | Where-Object { $_ -ne $folder } | Select-Object -First 2
        $recent += $existing
    }
    $recent | Set-Content $recentFile
}

Clear-Host
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║              CLAUDE CLI LAUNCHER                         ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Show recent folders first
$recentFolders = Get-RecentFolders
if ($recentFolders.Count -gt 0) {
    Write-Host "  RECENT:" -ForegroundColor Yellow
    $index = 1
    foreach ($recent in $recentFolders) {
        $displayName = Split-Path $recent -Leaf
        Write-Host "    [$index] $displayName" -ForegroundColor Green
        Write-Host "        $recent" -ForegroundColor DarkGray
        $index++
    }
    Write-Host ""
}

# Show project folders
Write-Host "  PROJECT FOLDERS:" -ForegroundColor Yellow
$startIndex = $recentFolders.Count + 1
for ($i = 0; $i -lt $folders.Count; $i++) {
    $num = $startIndex + $i
    Write-Host "    [$num] $($folders[$i].Name)" -ForegroundColor White
    Write-Host "        $($folders[$i].Path)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "  OTHER OPTIONS:" -ForegroundColor Yellow
Write-Host "    [C] Enter custom path" -ForegroundColor Magenta
Write-Host "    [Q] Quick start (default: CC Main)" -ForegroundColor Magenta
Write-Host "    [X] Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "  Select option"

$selectedPath = $null

switch -Regex ($choice.ToUpper()) {
    "^Q$" {
        $selectedPath = "C:\Users\peter\Downloads\CC"
    }
    "^X$" {
        Write-Host "`n  Goodbye!" -ForegroundColor Cyan
        exit
    }
    "^C$" {
        $customPath = Read-Host "  Enter folder path"
        if (Test-Path $customPath -PathType Container) {
            $selectedPath = $customPath
        } else {
            Write-Host "  Invalid path!" -ForegroundColor Red
            Start-Sleep -Seconds 2
            exit 1
        }
    }
    "^\d+$" {
        $num = [int]$choice
        $totalRecent = $recentFolders.Count

        if ($num -ge 1 -and $num -le $totalRecent) {
            # Recent folder selected
            $selectedPath = $recentFolders[$num - 1]
        } elseif ($num -ge ($totalRecent + 1) -and $num -le ($totalRecent + $folders.Count)) {
            # Project folder selected
            $folderIndex = $num - $totalRecent - 1
            $selectedPath = $folders[$folderIndex].Path
        } else {
            Write-Host "  Invalid selection!" -ForegroundColor Red
            Start-Sleep -Seconds 2
            exit 1
        }
    }
    default {
        Write-Host "  Invalid selection!" -ForegroundColor Red
        Start-Sleep -Seconds 2
        exit 1
    }
}

if ($selectedPath -and (Test-Path $selectedPath)) {
    # Save to recent
    Save-RecentFolder $selectedPath

    Write-Host ""
    Write-Host "  Starting Claude in: $selectedPath" -ForegroundColor Green
    Write-Host ""

    # Change to directory and start Claude
    Set-Location $selectedPath
    claude
} else {
    Write-Host "  Path not found: $selectedPath" -ForegroundColor Red
    Start-Sleep -Seconds 2
    exit 1
}
