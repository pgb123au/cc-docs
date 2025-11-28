"""
Claude Code Reminder Script
Beeps and shows notifications when Claude is waiting for user input.

Schedule:
- Every 1 minute for 5 minutes (5 reminders)
- Then every 15 minutes for 1 hour (4 reminders)
"""

import time
import winsound
from datetime import datetime
import sys

def beep_and_notify(message, reminder_num, total_reminders):
    """Play a beep sound and print notification"""
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Play Windows beep sound (frequency, duration in ms)
    # 1000 Hz for 500ms (half second)
    winsound.Beep(1000, 500)

    # Print to console
    print(f"\n{'='*60}")
    print(f"[{timestamp}] Reminder {reminder_num}/{total_reminders}")
    print(f"{message}")
    print(f"{'='*60}\n")

    # Try to show Windows notification using PowerShell
    try:
        import subprocess
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $notification = New-Object System.Windows.Forms.NotifyIcon
        $notification.Icon = [System.Drawing.SystemIcons]::Information
        $notification.Visible = $True
        $notification.BalloonTipTitle = "Claude Code Reminder"
        $notification.BalloonTipText = "{message}"
        $notification.ShowBalloonTip(5000)
        Start-Sleep -Seconds 6
        $notification.Dispose()
        """
        subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
                        creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        # If notification fails, just continue with beep
        print(f"(Notification failed: {e})")

def main():
    print("\n" + "="*60)
    print("CLAUDE CODE REMINDER SYSTEM STARTED")
    print("="*60)
    print("\nSchedule:")
    print("  - 5 reminders at 1-minute intervals (minutes 0-5)")
    print("  - 4 reminders at 15-minute intervals (minutes 20, 35, 50, 65)")
    print("\nPress Ctrl+C to stop at any time")
    print("="*60 + "\n")

    total_reminders = 9
    reminder_num = 0

    try:
        # Phase 1: Every 1 minute for 5 minutes
        for i in range(5):
            reminder_num += 1
            beep_and_notify(
                f"Claude Code is waiting for your input! (Minute {i+1}/5)",
                reminder_num,
                total_reminders
            )
            if i < 4:  # Don't sleep after the last one in this phase
                print(f"Next reminder in 1 minute... (Reminder {reminder_num+1}/{total_reminders})")
                time.sleep(60)  # 1 minute

        # Transition message
        print("\n" + "="*60)
        print("Phase 1 complete. Switching to 15-minute intervals...")
        print("="*60 + "\n")

        # Phase 2: Every 15 minutes for 1 hour (4 reminders)
        for i in range(4):
            reminder_num += 1
            beep_and_notify(
                f"Claude Code is still waiting! (15-min check {i+1}/4)",
                reminder_num,
                total_reminders
            )
            if i < 3:  # Don't sleep after the last one
                print(f"Next reminder in 15 minutes... (Reminder {reminder_num+1}/{total_reminders})")
                time.sleep(900)  # 15 minutes

        # Final message
        print("\n" + "="*60)
        print("ALL REMINDERS COMPLETE")
        print("Total elapsed time: ~65 minutes")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("Reminder system stopped by user")
        print(f"Completed {reminder_num}/{total_reminders} reminders")
        print("="*60 + "\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
