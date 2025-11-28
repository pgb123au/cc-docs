# How to Set Window Titles for Python Scripts

When you run Python scripts on Windows, you can customize the window title to show what's running.

## Method 1: In Your Scripts (Manual)

Add this at the top of any Python script:

```python
import os

# Set window title
if os.name == 'nt':  # Windows only
    os.system('title MyScriptName')
```

**Example:**
```python
import os
if os.name == 'nt':
    os.system('title Data Export')

# Rest of your script
print("Exporting data...")
```

## Method 2: Using the run.py Launcher

The `run.py` launcher **automatically** sets the window title to the script name when you run scripts through it!

- Before running: `title Python Script Launcher`
- While running: `title export_reignite_webhooks`
- After running: `title Python Script Launcher` (restored)

**No changes needed** - it just works!

## Method 3: Helper Function

Use the helper script for a more robust solution:

```python
from retell.Testing.CC-Made.CC-Made-set-window-title import set_window_title

# Auto-detects script name
set_window_title()

# Or use custom title
set_window_title("My Custom Title")
```

## For All Your Scripts

If you want **every** Python script to show its filename in the title automatically:

1. Create a file: `C:\Users\peter\sitecustomize.py`

2. Add this code:
```python
import os
import sys
from pathlib import Path

if os.name == 'nt':
    script_name = Path(sys.argv[0]).stem
    if script_name and script_name != 'python':
        os.system(f'title {script_name}')
```

3. Move to Python's site-packages:
   - Find location: `python -c "import site; print(site.getsitepackages()[0])"`
   - Copy `sitecustomize.py` there

**This runs automatically for every Python script!**

## Why This Matters

- Easy to identify which script is running in Task Manager
- Helpful when multiple Python windows are open
- Quick visual reference when switching between terminals

## Limitations

- **Windows only** - doesn't work on Mac/Linux
- Title only changes in the same window
- Scripts run in new windows need to set their own title
