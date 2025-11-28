# Making `run.bat` Available Globally

To run `run.bat` from any directory in Windows, you have two options:

## Option 1: Add CC Directory to PATH (Recommended)

1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", select "Path" and click "Edit"
5. Click "New" and add: `C:\Users\peter\Downloads\CC`
6. Click "OK" on all dialogs
7. **Restart your command prompt/terminal**
8. Now you can type `run` from any directory!

## Option 2: Copy to a PATH Directory

1. Copy `run-global.bat` to a directory already in your PATH, such as:
   - `C:\Windows\System32` (requires admin)
   - `C:\Users\peter\AppData\Local\Microsoft\WindowsApps` (no admin needed)

2. Rename it to just `run.bat`

3. Now you can type `run` from any directory!

## Verify It Works

1. Open a **new** Command Prompt or PowerShell window
2. Navigate to any directory: `cd C:\`
3. Type: `run`
4. The script launcher should appear!

## Notes

- After adding to PATH, you **must** restart your command prompt/terminal
- The script will always use the configuration from `C:\Users\peter\Downloads\CC\run_config.json`
- Scripts will run in the directory you select in the menu, not your current directory
