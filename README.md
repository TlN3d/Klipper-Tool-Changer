# Klipper-Tool-Changer

Klipper-Tool-Changer is a script that automatically changes config settings depending on resistance over a pin.

# Description

Automation that listens to stored values from Klipper and activates a .cfg file accordingly. 

### My use case:
I made it to be able to change rotation distance when changing between a normal extruder and [GreenBoy3D's pellet extruder](https://greenboy3d.de). Each extruder attaches to the printhead magnetically, wires are connected using magnetic pin connectors. A different resistor on each extruder is connected to a free pin and a GND line of a fan. I have the gcode macro `IDENTIFY_TOOL` in my `print_start` macro in case I forget to run it manually.

### How it works:
* Gcode macro `IDENTIFY_TOOL` tests resistance of a resistor connected to selected pin and GND.
* Klipper processes the given input depending on set intervals and assigns a value to `toolid`.
* That value then gets stored to `/home/user/printer_data/ToolChanger/tool_state.cfg`.
* A systemd service runs python script on startup.
* On change in `tool_state.cfg` the script `tool_watcher.py` (ran from startup by a systemd service `tool_watcher.service`) reads the value in `tool_change.cfg` and chooses the corresponding file from `/home/user/printer_data/config/Tools`.
* That file then gets copied, renamed to `tool.cfg` and moved to `/home/user/printer_data/config`, where it can be called by `printer.cfg`.
* The original file stays in its original location unchanged.
* Klipper service restarts.

> **Note:**
> The script was tested only on the BIQU BTTPi. The RaspberryPi version is untested. If anyone tries it I would greatly appreciate any feedback.


# Installation
To install onto a BTTPi, use files in the `Biqu` folder. To install onto a RaspberryPi or similar, use files in the `RaspberryPi` folder. The only differences are paths in `tool_watcher.service` and `tool_watcher.py`.

### System setup:

1. Move the map ToolChager to `/home/user/printer_data/` with [WinSCP](https://winscp.net/eng/download.php) or a similar tool. Alternatively you can `ssh` into your device and run either:
   ```bash
   sudo mkdir /home/biqu/printer_data/ToolChanger
   sudo nano /home/biqu/printer_data/ToolChanger/tool_watcher.py
   ```
   ***or***
   ```bash
   sudo mkdir /home/pi/printer_data/ToolChanger
   sudo nano /home/pi/printer_data/ToolChanger/tool_watcher.py
   ```
   and paste the contents of the correct `tool_watcher.py`.

2. Make it executable:
   ```bash
   chmod +x /home/biqu/printer_data/ToolChanger/tool_watcher.py
   ```
   ***or***
   ```bash
   chmod +x /home/pi/printer_data/ToolChanger/tool_watcher.py
   ```
   
3. Move `tool_watcher.service` to `/etc/systemd/system/` ***or*** run:
   ```bash
   sudo nano /etc/systemd/system/tool_watcher.service
   ```
   and paste the contents of the correct `tool_watcher.service`.
   
4. Run commands:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now tool_watcher.service
   ```
		
5. You can check service's status with the command:
   ```bash
   systemctl status tool_watcher.service
   ```
		
### Klipper setup:

1. Create a section for the sensor in `printer.cfg` with the correct pins:
   ```yaml
   [adc_temperature resistance_sensor]
	voltage1: 0
	temperature1: 0
	voltage2: 5
	temperature2: 500

	[temperature_sensor toolid]
	sensor_type: resistance_sensor
	sensor_pin: EXAMPLE_PIN
	min_temp: 0
	max_temp: 500
   ```

2. Include `tool.cfg` in `printer.cfg`:
   ```yaml
   [include tool.cfg]
   ```
	
3. Create a gcode macro that reads the data from `toolid` and saves its values:
   ```yaml
   [save_variables]
	filename: /home/biqu/printer_data/ToolChanger/tool_state.cfg
	
	[gcode_macro IDENTIFY_TOOL]
	gcode:
	    {% set v = printer['temperature_sensor toolid'].temperature %}
	    {% if v > 14 and v < 18 %}
	        RESPOND MSG="TOOL 1"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=1
 	   {% elif v > 350 and v < 365 %}
 	       RESPOND MSG="TOOL 2"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=2
 	   {% elif v > 420 and v < 430 %}
 	       RESPOND MSG="TOOL 3"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=3
 	   {% else %}
 	       RESPOND MSG="NO TOOL DETECTED"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=0
 	   {% endif %}
   ```
   ***or***
   ```yaml
   [save_variables]
	filename: /home/pi/printer_data/ToolChanger/tool_state.cfg
	
	[gcode_macro IDENTIFY_TOOL]
	gcode:
	    {% set v = printer['temperature_sensor toolid'].temperature %}
	    {% if v > 14 and v < 18 %}
	        RESPOND MSG="TOOL 1"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=1
 	   {% elif v > 350 and v < 365 %}
 	       RESPOND MSG="TOOL 2"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=2
 	   {% elif v > 420 and v < 430 %}
 	       RESPOND MSG="TOOL 3"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=3
 	   {% else %}
 	       RESPOND MSG="NO TOOL DETECTED"
 	       SAVE_VARIABLE VARIABLE=tool VALUE=0
 	   {% endif %}
   ```
   Don't forget to modify the intervals so that they correspond to different tools/resistors.

4. Create different .cfg files in `/home/user/printer_data/config/Tools` named `tool1.cfg`, `tool2.cfg` or `tool3.cfg`. If more files are needed, duplicate a section in the gcode macro in step 3 above and add a line with file name and value in tool_watcher.py (lines 10-12).

5. Run gcode macro `IDENTIFY_TOOL`.
