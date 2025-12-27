#!/usr/bin/env python3
import os, time, shutil, requests

CONFIG_DIR = "/home/biqu/printer_data/config"
TEMPLATE_DIR = "/home/biqu/printer_data/config/Tools"
ACTIVE_FILE = "/home/biqu/printer_data/config/tool.cfg"
STATE_FILE = "/home/biqu/printer_data/ToolChanger/tool_state.cfg"

TOOLS = {
    1: "tool1.cfg",
    2: "tool2.cfg",
    3: "tool3.cfg"
}

MOONRAKER_URL = "http://localhost:7125/server/restart"

def read_tool():
    """Read the 'tool =' line from tool_state.cfg."""
    try:
        with open(STATE_FILE) as f:
            for line in f:
                if line.strip().startswith("tool"):
                    return int(line.split("=")[1])
    except FileNotFoundError:
        return 0
    return 0

def restart_klipper():
    """Tell Moonraker to restart Klipper."""
    try:
        requests.post(MOONRAKER_URL, timeout=5)
    except Exception as e:
        print("Restart failed:", e)

def copy_template(tool):
    """Duplicate and replace printer.cfg safely."""
    template = os.path.join(TEMPLATE_DIR, TOOLS[tool])
    backup = ACTIVE_FILE + ".bak"
    shutil.copy2(ACTIVE_FILE, backup)
    shutil.copy2(template, ACTIVE_FILE)
    print(f"Tool {tool}: template copied to printer.cfg")

def main():
    current = None
    while True:
        tool = read_tool()
        if tool != current and tool in TOOLS:
            copy_template(tool)
            restart_klipper()
            current = tool
        time.sleep(5)

if __name__ == "__main__":
    main()
