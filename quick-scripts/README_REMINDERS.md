# Claude Code Reminder System

## Purpose
Beeps and shows notifications when Claude Code is waiting for your input.

## Files
- `claude_reminder.py` - Main Python script
- `START_CLAUDE_REMINDERS.bat` - Double-click to run easily

## Schedule
1. **Phase 1 (First 5 minutes):**
   - Beeps every 1 minute
   - 5 total reminders

2. **Phase 2 (Next 60 minutes):**
   - Beeps every 15 minutes
   - 4 total reminders

**Total duration:** ~65 minutes (9 reminders)

## How to Use

### Option 1: Double-click batch file (easiest)
1. Double-click `START_CLAUDE_REMINDERS.bat`
2. Leave the window open (you can minimize it)
3. You'll hear beeps and see notifications
4. Press Ctrl+C in the window to stop early

### Option 2: Run Python directly
```bash
python claude_reminder.py
```

## Features
- **Sound:** Windows beep sound (1000 Hz for 500ms)
- **Notifications:** Windows toast notifications with "Claude Code Reminder" title
- **Console output:** Shows timestamp and reminder number
- **Interrupt:** Press Ctrl+C to stop anytime

## System Requirements
- Windows OS (uses `winsound` and PowerShell notifications)
- Python 3.x installed

## Example Output
```
============================================================
CLAUDE CODE REMINDER SYSTEM STARTED
============================================================

Schedule:
  - 5 reminders at 1-minute intervals (minutes 0-5)
  - 4 reminders at 15-minute intervals (minutes 20, 35, 50, 65)

Press Ctrl+C to stop at any time
============================================================

============================================================
[14:23:15] Reminder 1/9
Claude Code is waiting for your input! (Minute 1/5)
============================================================

Next reminder in 1 minute... (Reminder 2/9)
```

## Notes
- Minimize the console window if you want it out of the way
- The script will automatically exit after all 9 reminders
- If notifications don't show, you'll still hear the beeps
- You can run multiple instances if needed

---
Created: 2025-11-23
