# Helper script to organize your existing files
# Edit the paths below to match your actual files

$Downloads = "$env:USERPROFILE\Downloads"
$Projects = "$env:USERPROFILE\Downloads\claude-projects"

# Example moves (uncomment and customize):
# Move-Item "$Downloads\*.py" "$Projects\quick-scripts\"
# Move-Item "$Downloads\retell*.json" "$Projects\agents\reignite-receptionist\configs\"
# Move-Item "$Downloads\Python\*" "$Projects\learning\python-experiments\"
# Move-Item "$Downloads\n8n\*" "$Projects\n8n-workflows\"

Write-Host "Edit this script first to match your actual files!" -ForegroundColor Yellow
