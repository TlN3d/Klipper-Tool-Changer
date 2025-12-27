# Klipper-Tool-Changer

Klipper-Tool-Changer is a script that automatically changes config settings depending on resistance over a pin.

# Description

Automation that listens to stored values from Klipper and activates a .cfg file accordingly.

* Pin tests resistance of a resistor connected to it and GND.
* Klipper stores the given value to `/home/user/printer_data/ToolChanger/tool_state.cfg`.
* A systemd service runs python script in `/home/user/printer_data/ToolChanger/tool_watcher.py` on startup.
* On change in `tool_state.cfg` the script reads the value in `tool_change.cfg` and chooses the correct file from `/home/user/printer_data/config/Tools`.
* That file then gets copied, renamed to `tool.cfg` and moved to `/home/user/printer_data/config`, where it can be called by `printer.cfg`.
* The original file stays in its original location unchanged. Klipper service restarts.
> *Note:*
> The script was tested only on the BIQU BTTPi. The RaspberryPi version is untested. If anyone tries it I would greatly appreciate any feedback.

# Installation

### System setup:

1. Move the map ToolChager to `/home/user/printer_data/` with [WinSCP](https://winscp.net/eng/download.php) or a similar tool. Alternatively you can `ssh` into your device and run either:
   ```bash
   sudo mkdir /home/biqu/printer_data/ToolChanger
   sudo nano /home/biqu/printer_data/ToolChanger/tool_watcher.py
   ```
   or
   ```bash
   sudo mkdir /home/pi/printer_data/ToolChanger
   sudo nano /home/pi/printer_data/ToolChanger/tool_watcher.py
   ```
   and paste the contents of the correct tool_watcher.py from this repository.
3. Move tool_watcher.service to /etc/systemd/system
4. Run commands: 
sudo systemctl daemon-reload
sudo systemctl enable --now tool_watcher.service
		
	4. You can check service's status with the command:
systemctl status tool_watcher.service
		
---
II. Klipper setup:

	1. Create a section for the sensor in printer.cfg:
[adc_temperature my_sensor_type]
voltage1: 0
temperature1: 0
voltage2: 5
temperature2: 500

[temperature_sensor headid]
sensor_type: my_sensor_type
sensor_pin: PA4
min_temp: 0
max_temp: 500

	2. Include tool.cfg in printer.cfg:
[include tool.cfg]
	
	3. Create gcode macro that reads the data from headid and saves its values:
[save_variables]
filename: /home/biqu/printer_data/ToolChanger/tool_state.cfg

[gcode_macro IDENTIFY_TOOL]
gcode:
    {% set v = printer['temperature_sensor headid'].temperature %}
    {% if v > 14 and v < 18 %}
        RESPOND MSG="TOOL 1"
        SAVE_VARIABLE VARIABLE=tool VALUE=1
    {% elif v > 350 and v < 365 %}
        RESPOND MSG="TOOL 2"
        SAVE_VARIABLE VARIABLE=tool VALUE=2
    {% elif v > 420 and v < 430 %}
        RESPOND MSG="TOOL 3"
        SAVE_VARIABLE VARIABLE=tool VALUE=3
    {% elif v > 445 and v < 455 %}
        RESPOND MSG="TOOL 4"
        SAVE_VARIABLE VARIABLE=tool VALUE=4
    {% else %}
        RESPOND MSG="NO TOOL DETECTED"
        SAVE_VARIABLE VARIABLE=tool VALUE=0
    {% endif %}

	4. Create different .cfg files in /home/biqu/printer_data/config/Tools named tool1.cfg, tool2.cfg,
	tool3.cfg or tool4.cfg. If more files are needed, duplicate a section in the gcode macro (lines
	48-59 in this file) and add a line with file name and value in tool_watcher.py (lines 10-12)
