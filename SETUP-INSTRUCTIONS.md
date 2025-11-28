# Quick Setup - Add to PATH

## Step 1: Run the Setup Script

**Double-click:** `SETUP-PATH.bat`

This will add `C:\Users\peter\Downloads\CC` to your User PATH environment variable.

## Step 2: Restart Your Terminal

**IMPORTANT:** Close and reopen your Command Prompt or PowerShell window.

Changes to PATH only take effect in new terminal sessions!

## Step 3: Test It

Open a **new** terminal window and try:

```cmd
cd C:\
run
```

You should see the Python Script Launcher menu!

## What This Does

- Adds `C:\Users\peter\Downloads\CC` to your User PATH
- Allows you to run `run.bat` from any directory
- Does NOT require administrator privileges
- Only affects your user account (not system-wide)

## If It Doesn't Work

1. Make sure you restarted your terminal
2. Check PATH was added:
   ```powershell
   $env:PATH -split ';' | Select-String "CC"
   ```
3. If still not working, run manually:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "C:\Users\peter\Downloads\CC\add-to-path.ps1"
   ```

## To Remove Later

If you want to remove this from PATH:

1. Press `Win + X` → System
2. Advanced system settings → Environment Variables
3. Edit User PATH
4. Remove the `C:\Users\peter\Downloads\CC` entry
