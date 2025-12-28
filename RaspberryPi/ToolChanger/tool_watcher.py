
#!/usr/bin/env python3
import os, time, shutil, requests

CONFIG_DIR = "/home/pi/printer_data/config"
TEMPLATE_DIR = "/home/pi/printer_data/config/Tools"
ACTIVE_FILE = "/home/pi/printer_data/config/tool.cfg"
STATE_FILE = "/home/pi/printer_data/ToolChanger/tool_state.cfg"

TOOLS = {
    1: "tool1.cfg",
    2: "tool2.cfg",
    3: "tool3.cfg"
}

MOONRAKER_URL = "http://localhost:7125/server/restart"

def read_tool():
    """Read the 'tool =' line from tool_state.cfg."""
    if not os.path.exists(STATE_FILE):
        print("ERROR: tool_state.cfg not found")
        return None

    try:
        with open(STATE_FILE) as f:
            for line in f:
                if line.strip().startswith("tool"):
                    value = int(line.split("=")[1])
                    if value == 0:
                        print("INFO: no tool attached")
                    return value
        print("ERROR: tool variable not found in tool_state.cfg")
        return None
    except Exception as e:
        print("ERROR: failed to read tool_state.cfg:", e)
        return None
 
def restart_klipper():
    """Tell Moonraker to restart Klipper."""
    try:
        requests.post(MOONRAKER_URL, timeout=5)
    except Exception as e:
        print("ERROR: Klipper restart failed:", e)

def copy_template(tool):
    """Duplicate and replace printer.cfg safely."""
    template = os.path.join(TEMPLATE_DIR, TOOLS[tool])
    backup = ACTIVE_FILE + ".bak"
    shutil.copy2(ACTIVE_FILE, backup)
    shutil.copy2(template, ACTIVE_FILE)
    print(f"tool{tool}.cfg activated successfully.")

def main():
    current = None
    while True:
        tool = read_tool()

        if tool is None:
            time.sleep(10)
            continue

        if tool not in TOOLS:
            print(f"WARNING: tool {tool} has no matching config")
            time.sleep(10)
            continue

        if tool != current:
            copy_template(tool)
            restart_klipper()
            current = tool

        time.sleep(5)


if __name__ == "__main__":
    main()
