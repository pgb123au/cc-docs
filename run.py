#!/usr/bin/env python3
"""
Python Script Launcher - Interactive Menu System
Organizes and runs Python scripts from across the codebase.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import json
import shutil

# Configuration file for default working directory
CONFIG_FILE = "run_config.json"

# Color codes for terminal output (Windows compatible)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_script_categories() -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Organize all Python scripts by category/folder.
    Returns dict: {category_name: [(script_name, full_path, relative_path), ...]}
    """
    base_dir = Path(__file__).parent

    scripts = {
        "Launcher Scripts": [],
        "n8n - Core Scripts": [],
        "n8n - Diagnostics": [],
        "RetellAI - API Scripts": [],
        "RetellAI - Testing & Fixes": [],
        "RetellAI - Audit": [],
        "Other": []
    }

    def get_rel_path(full_path):
        """Get relative path from base directory"""
        try:
            return str(Path(full_path).relative_to(base_dir))
        except:
            return str(Path(full_path).name)

    # Launcher Scripts (run.py and run.bat)
    run_py = base_dir / "run.py"
    run_bat = base_dir / "run.bat"
    if run_py.exists():
        scripts["Launcher Scripts"].append((run_py.name, str(run_py), get_rel_path(run_py)))
    if run_bat.exists():
        scripts["Launcher Scripts"].append((run_bat.name, str(run_bat), get_rel_path(run_bat)))

    # n8n Core Scripts
    n8n_python = base_dir / "n8n" / "Python"
    if n8n_python.exists():
        for script in sorted(n8n_python.glob("*.py")):
            scripts["n8n - Core Scripts"].append((script.name, str(script), get_rel_path(script)))

    # n8n Diagnostics
    n8n_diag = base_dir / "n8n" / "Python" / "Diagnose-n8n-Errors"
    if n8n_diag.exists():
        for script in sorted(n8n_diag.glob("*.py")):
            scripts["n8n - Diagnostics"].append((script.name, str(script), get_rel_path(script)))

    # RetellAI API Scripts - key upload/download scripts
    retell_api_scripts = base_dir / "retell" / "archive" / "agent-history" / "testing-root-old"
    if retell_api_scripts.exists():
        # Add specific key API scripts
        upload_script = retell_api_scripts / "upload_retellai_v1-03.py"
        calls_script = retell_api_scripts / "download_retellai_calls_v1-00.py"
        agents_script = retell_api_scripts / "download_retellai_agents_v1-00.py"

        if upload_script.exists():
            scripts["RetellAI - API Scripts"].append((upload_script.name, str(upload_script), get_rel_path(upload_script)))
        if calls_script.exists():
            scripts["RetellAI - API Scripts"].append((calls_script.name, str(calls_script), get_rel_path(calls_script)))
        if agents_script.exists():
            scripts["RetellAI - API Scripts"].append((agents_script.name, str(agents_script), get_rel_path(agents_script)))

    # RetellAI Testing - main folder (exclude CC-Made subfolder)
    retell_testing = base_dir / "retell" / "Testing"
    if retell_testing.exists():
        for script in sorted(retell_testing.glob("*.py")):
            if "audit" in script.name.lower():
                scripts["RetellAI - Audit"].append((script.name, str(script), get_rel_path(script)))
            else:
                scripts["RetellAI - Testing & Fixes"].append((script.name, str(script), get_rel_path(script)))

    # Remove empty categories
    scripts = {k: v for k, v in scripts.items() if v}

    return scripts

def load_config() -> dict:
    """Load configuration from JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"default_working_dir": os.getcwd()}

def save_config(config: dict):
    """Save configuration to JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def display_menu(scripts: Dict[str, List[Tuple[str, str, str]]], config: dict):
    """Display the interactive menu."""
    terminal_width = shutil.get_terminal_size((120, 50)).columns
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*terminal_width}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Python Script Launcher  {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*terminal_width}{Colors.ENDC}\n")

    # Show current working directory
    current_dir = config.get("default_working_dir", os.getcwd())
    print(f"{Colors.YELLOW}Default run directory: {Colors.ENDC}{current_dir}\n")

    # Build numbered list
    index = 1
    script_map = {}

    # Calculate column widths based on terminal size
    # 1/3 for filename, rest for full path
    filename_col_width = terminal_width // 3
    path_col_width = terminal_width - filename_col_width - 8  # -8 for index number and spacing

    for category, script_list in scripts.items():
        print(f"{Colors.BOLD}{Colors.HEADER}[{category}]{Colors.ENDC}")

        # Header row
        print(f"  {Colors.BOLD}{'#':<4} {'Filename':<{filename_col_width}}  {'Full Path':<{path_col_width}}{Colors.ENDC}")
        print(f"  {Colors.BOLD}{'-'*4} {'-'*filename_col_width}  {'-'*path_col_width}{Colors.ENDC}")

        # Display in two columns: Filename | Full Path
        for name, path, rel_path in script_list:
            # Truncate if too long
            display_name = name if len(name) <= filename_col_width else name[:filename_col_width-3] + "..."
            display_path = path if len(path) <= path_col_width else "..." + path[-(path_col_width-3):]

            print(f"  {Colors.GREEN}{index:2d}.{Colors.ENDC} {display_name:<{filename_col_width}}  {Colors.CYAN}{display_path}{Colors.ENDC}")
            script_map[index] = (name, path, rel_path)
            index += 1

        print()

    # Menu options
    print(f"{Colors.BOLD}{Colors.BLUE}Options:{Colors.ENDC}")
    print(f"  {Colors.CYAN}e.{Colors.ENDC} Edit script in Claude")
    print(f"  {Colors.CYAN}r.{Colors.ENDC} Refresh script list")
    print(f"  {Colors.CYAN}c.{Colors.ENDC} Change default working directory")
    print(f"  {Colors.CYAN}q.{Colors.ENDC} Quit")
    print()

    # Claude Code shortcuts
    print(f"{Colors.BOLD}{Colors.BLUE}Run Claude Code:{Colors.ENDC}")
    print(f"  {Colors.CYAN}cc.{Colors.ENDC}  Run Claude in C:\\Users\\peter\\Downloads\\CC\\")
    print(f"  {Colors.CYAN}ccr.{Colors.ENDC} Run Claude in C:\\Users\\peter\\Downloads\\CC\\retell\\")
    print(f"  {Colors.CYAN}ccn.{Colors.ENDC} Run Claude in C:\\Users\\peter\\Downloads\\CC\\n8n\\")
    print()

    # Telco Manager
    print(f"{Colors.BOLD}{Colors.BLUE}Telco:{Colors.ENDC}")
    print(f"  {Colors.CYAN}t.{Colors.ENDC}   Telco Manager (Zadarma, Telnyx, Retell)")
    print()

    return script_map

def change_working_directory(config: dict):
    """Change the default working directory."""
    print(f"\n{Colors.YELLOW}Current working directory: {Colors.ENDC}{config.get('default_working_dir', os.getcwd())}")
    new_dir = input(f"{Colors.CYAN}Enter new working directory (or press Enter to cancel): {Colors.ENDC}").strip()

    if new_dir:
        new_dir = os.path.abspath(os.path.expanduser(new_dir))
        if os.path.isdir(new_dir):
            config["default_working_dir"] = new_dir
            save_config(config)
            print(f"{Colors.GREEN}Working directory updated to: {new_dir}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Error: Directory does not exist!{Colors.ENDC}")

def suggest_paths(script_path: str, script_name: str, rel_path: str, config: dict):
    """Suggest likely working directories for the script."""
    base_dir = Path(__file__).parent
    script_dir = Path(script_path).parent

    suggested = []

    # 1. Default configured directory
    suggested.append(("Default", config.get("default_working_dir", str(base_dir))))

    # 2. Script's own directory
    if str(script_dir) != config.get("default_working_dir"):
        suggested.append(("Script's directory", str(script_dir)))

    # 3. Root directory (if not already added)
    if str(base_dir) not in [s[1] for s in suggested]:
        suggested.append(("Root (CC/)", str(base_dir)))

    # 4. Specific suggestions based on script location
    if "n8n" in rel_path.lower():
        n8n_python = base_dir / "n8n" / "Python"
        if n8n_python.exists() and str(n8n_python) not in [s[1] for s in suggested]:
            suggested.append(("n8n/Python/", str(n8n_python)))

    if "retell" in rel_path.lower():
        retell_testing = base_dir / "retell" / "Testing"
        if retell_testing.exists() and str(retell_testing) not in [s[1] for s in suggested]:
            suggested.append(("retell/Testing/", str(retell_testing)))

    return suggested

def select_working_directory(script_path: str, script_name: str, rel_path: str, config: dict):
    """Show menu to select working directory."""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}Select working directory:{Colors.ENDC}\n")

    suggested = suggest_paths(script_path, script_name, rel_path, config)

    for i, (label, path) in enumerate(suggested, 1):
        print(f"  {Colors.GREEN}{i}.{Colors.ENDC} {label:20s} {Colors.CYAN}{path}{Colors.ENDC}")

    print(f"  {Colors.GREEN}0.{Colors.ENDC} {'Custom path':20s} {Colors.CYAN}(enter manually){Colors.ENDC}")
    print()

    while True:
        choice = input(f"{Colors.BOLD}Select directory (1-{len(suggested)}, or 0 for custom): {Colors.ENDC}").strip()

        try:
            choice_num = int(choice)
            if choice_num == 0:
                custom = input(f"{Colors.CYAN}Enter custom path: {Colors.ENDC}").strip()
                custom = os.path.abspath(os.path.expanduser(custom))
                if os.path.isdir(custom):
                    return custom
                else:
                    print(f"{Colors.RED}Invalid directory!{Colors.ENDC}")
                    continue
            elif 1 <= choice_num <= len(suggested):
                return suggested[choice_num - 1][1]
            else:
                print(f"{Colors.RED}Invalid choice!{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Please enter a number!{Colors.ENDC}")

def run_script(script_path: str, script_name: str, working_dir: str):
    """Run the selected Python script."""
    terminal_width = shutil.get_terminal_size((120, 50)).columns

    # Set window title to script name (shortened)
    short_name = script_name.replace('.py', '')
    if len(short_name) > 50:
        short_name = short_name[:47] + "..."

    # Change window title
    if os.name == 'nt':  # Windows
        os.system(f'title {short_name}')

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*terminal_width}{Colors.ENDC}")
    print(f"{Colors.BOLD}Running: {Colors.GREEN}{script_name}{Colors.ENDC}")
    print(f"{Colors.BOLD}Path: {Colors.ENDC}{script_path}")
    print(f"{Colors.BOLD}Working Dir: {Colors.ENDC}{working_dir}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*terminal_width}{Colors.ENDC}\n")

    try:
        # Run the script in the specified working directory
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=working_dir,
            check=False
        )

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*terminal_width}{Colors.ENDC}")
        if result.returncode == 0:
            print(f"{Colors.GREEN}Script completed successfully!{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Script exited with code {result.returncode}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*terminal_width}{Colors.ENDC}\n")

    except Exception as e:
        print(f"{Colors.RED}Error running script: {e}{Colors.ENDC}\n")

    # Reset window title back to launcher
    if os.name == 'nt':
        os.system('title Python Script Launcher')

    input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")

def main():
    """Main interactive loop."""
    config = load_config()

    while True:
        # Clear screen (Windows/Unix compatible)
        os.system('cls' if os.name == 'nt' else 'clear')

        # Get and display scripts
        scripts = get_script_categories()
        script_map = display_menu(scripts, config)

        # Get user input
        choice = input(f"{Colors.BOLD}Enter number to run script (or 'e'/'r'/'c'/'q'): {Colors.ENDC}").strip().lower()

        if choice == 'q':
            print(f"\n{Colors.CYAN}Goodbye!{Colors.ENDC}\n")
            break
        elif choice == 'r':
            print(f"{Colors.GREEN}Refreshing script list...{Colors.ENDC}")
            continue
        elif choice == 'c':
            change_working_directory(config)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        elif choice == 'cc':
            claude_dir = r"C:\Users\peter\Downloads\CC"
            print(f"\n{Colors.GREEN}Opening Claude in {claude_dir}...{Colors.ENDC}\n")
            subprocess.run(["claude"], cwd=claude_dir, check=False)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        elif choice == 'ccr':
            claude_dir = r"C:\Users\peter\Downloads\CC\retell"
            print(f"\n{Colors.GREEN}Opening Claude in {claude_dir}...{Colors.ENDC}\n")
            subprocess.run(["claude"], cwd=claude_dir, check=False)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        elif choice == 'ccn':
            claude_dir = r"C:\Users\peter\Downloads\CC\n8n"
            print(f"\n{Colors.GREEN}Opening Claude in {claude_dir}...{Colors.ENDC}\n")
            subprocess.run(["claude"], cwd=claude_dir, check=False)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        elif choice == 't':
            telco_dir = r"C:\Users\peter\Downloads\CC\Telcos"
            telco_script = os.path.join(telco_dir, "telco.py")
            print(f"\n{Colors.GREEN}Opening Telco Manager...{Colors.ENDC}\n")
            subprocess.run([sys.executable, telco_script], cwd=telco_dir, check=False)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        elif choice == 'e':
            script_num_str = input(f"{Colors.YELLOW}Enter script number to edit: {Colors.ENDC}").strip()
            try:
                script_num = int(script_num_str)
                if script_num in script_map:
                    name, path, rel_path = script_map[script_num]
                    script_dir = os.path.dirname(path)

                    print(f"\n{Colors.GREEN}Opening {name} in Claude...{Colors.ENDC}")
                    print(f"{Colors.CYAN}Directory: {script_dir}{Colors.ENDC}\n")

                    # Open Claude Code in the script's directory with the file
                    subprocess.run(["claude", path], cwd=script_dir, check=False)

                    input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Invalid script number!{Colors.ENDC}")
                    input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number!{Colors.ENDC}")
                input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue

        # Try to parse as number
        try:
            script_num = int(choice)
            if script_num in script_map:
                name, path, rel_path = script_map[script_num]

                # Select working directory from menu
                working_dir = select_working_directory(path, name, rel_path, config)

                run_script(path, name, working_dir)
            else:
                print(f"{Colors.RED}Invalid number!{Colors.ENDC}")
                input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Invalid input!{Colors.ENDC}")
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Interrupted by user. Goodbye!{Colors.ENDC}\n")
        sys.exit(0)
