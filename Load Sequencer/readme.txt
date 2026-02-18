# Load Sequencer Simulator

A Python-based simulator for controlling electrical loads via Modbus RTU communication. The simulator supports two operation modes: **Periodic** testing and **Sequence** testing.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [JSON Templates](#json-templates)
- [Hardware Requirements](#hardware-requirements)
- [Troubleshooting](#troubleshooting)

## Features

- **Periodic Mode**: Control meters with duty cycles (percentage on-time over a period)
- **Sequence Mode**: Time-based meter control with scheduled state changes
- **On-Demand Initialization**: Meters are only initialized when needed
- **Multiple Sets**: Run multiple meter groups simultaneously in separate threads
- **Real-time Monitoring**: Display current status and next scheduled actions
- **Graceful Shutdown**: Clean disconnect from all Modbus devices

## Installation

1. **Create Virtual Environment**:
```bash
cd "/home/main/Desktop/Load Sequencer"
python3 -m venv .venv
source .venv/bin/activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Required Dependencies**:
```txt
pyserial>=3.5
minimalmodbus>=2.0.1
jsonpickle>=3.0.0
```

## Configuration

### Directory Structure
```
Load Sequencer/
├── simulator.py
├── tv_tools.py
├── requirements.txt
├── Configs/
│   └── meter_config.json
├── Periodics/
│   └── periodic_test.json
└── Sequenced/
    └── sequence_test.json
```

### Meter Configuration
Create `Configs/meter_config.json` with your meter addresses:

```json
{
    "Grid": 4,
    "G6K2 Ess-Var": 8,
    "G6K2 NEss": 5,
    "PV Ess-Var": 9,
    "PV NEss": 6
}
```

## Usage

### Running the Simulator

```bash
# Activate virtual environment
source .venv/bin/activate

# Run periodic mode
python simulator.py --mode periodic

# Run sequence mode
python simulator.py --mode sequence
```

### Periodic Mode
- Select a configuration file from the `Periodics/` folder
- Each set runs in a separate thread
- Meters cycle between ON/OFF based on duty cycle and period
- Press `Ctrl+C` to stop

### Sequence Mode
- Select a configuration file from the `Sequenced/` folder
- Initializes meters based on the last timestamp before current time
- Executes actions at scheduled times
- Shows current time and next scheduled action
- Press `Ctrl+C` to stop

## JSON Templates

### Periodic Test Template

Save as `Periodics/your_test.json`:

```json
{
    "Description": "Your Periodic Test Description",
    "Version": "1.0",
    "Author": "Your Name",
    "Help": "This file defines a periodic test for the Load Sequencer. Period is in Minutes and Duty is Percentage of Period On",
    "Sets": {
        "Set_Name_1": {
            "Meter_Name_1": {
                "Duty": 70,
                "Period": 510
            },
            "Meter_Name_2": {
                "Duty": 50,
                "Period": 120
            }
        },
        "Set_Name_2": {
            "Meter_Name_3": {
                "Duty": 30,
                "Period": 60
            }
        }
    }
}
```

**Parameters:**
- `Duty`: Percentage of time the meter should be ON (0-100)
- `Period`: Total cycle time in minutes
- `Set_Name`: Descriptive name for the group of meters
- `Meter_Name`: Must match names in `meter_config.json`

**Example Calculation:**
- Duty: 70%, Period: 510 minutes
- ON time: 510 × 0.70 = 357 minutes
- OFF time: 510 - 357 = 153 minutes

### Sequence Test Template

Save as `Sequenced/your_test.json`:

```json
{
    "Description": "Your Sequence Test Description",
    "Version": "1.0",
    "Author": "Your Name",
    "Help": "This file defines a sequence test with time-based meter control. Time format is HH:MM (24-hour)",
    "Sequence": {
        "00:00": {
            "Meter_Name_1": "Off",
            "Meter_Name_2": "Off"
        },
        "08:00": {
            "Meter_Name_1": "On",
            "Meter_Name_2": "On"
        },
        "12:00": {
            "Meter_Name_1": "Off"
        },
        "18:00": {
            "Meter_Name_1": "On",
            "Meter_Name_2": "Off"
        },
        "22:00": {
            "Meter_Name_1": "Off",
            "Meter_Name_2": "Off"
        }
    }
}
```

**Parameters:**
- `Time`: 24-hour format (HH:MM)
- `Meter_Name`: Must match names in `meter_config.json`
- `State`: "On", "Off", "True", "False", "1", "0" (case-insensitive)

**Behavior:**
- On startup, finds the last timestamp before current time and applies those states
- Monitors for scheduled time changes every 30 seconds
- Displays current time and next scheduled change

## Hardware Requirements

- **USB-to-RS485 Adapter**: Typically appears as `/dev/ttyUSB0`
- **Modbus RTU Devices**: Connected via RS485 bus
- **Linux System**: Tested on Ubuntu/Debian systems

### Serial Port Configuration
The simulator uses these default settings:
- Baudrate: 9600
- Data bits: 8
- Parity: None
- Stop bits: 1
- Timeout: 1.0 second

## Troubleshooting

### Common Issues

1. **"No JSON configuration files found"**
   - Ensure files are in correct folders (`Periodics/` or `Sequenced/`)
   - Check file extensions are `.json`

2. **"Meter X not found in meter_config.json"**
   - Verify meter names match exactly between test files and `meter_config.json`
   - Check for typos and case sensitivity

3. **"Failed to initialize meter at address X"**
   - Check USB-to-RS485 adapter connection
   - Verify Modbus device is powered and connected
   - Confirm correct Modbus address
   - Check `/dev/ttyUSB0` permissions: `sudo chmod 666 /dev/ttyUSB0`

4. **"Communication test failed"**
   - Verify serial port exists: `ls /dev/ttyUSB*`
   - Check if another application is using the port
   - Confirm Modbus device settings match simulator configuration

5. **"Permission denied" on serial port**
   ```bash
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

### Debug Mode
For detailed communication logs, modify `tv_tools.py`:
```python
instrument.debug = True  # Enable debug output
```

### Testing Without Hardware
To test configuration files without Modbus hardware, comment out the Modbus communication in `tv_tools.py` and return mock objects.

## File Validation

Before running, ensure:
- All meter names in test files exist in `meter_config.json`
- JSON files are valid (no syntax errors)
- Time formats in sequence files are HH:MM
- Duty cycles are 0-100%
- Periods are positive numbers

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify hardware connections
3. Validate JSON configuration files
4. Check system logs: `dmesg | grep ttyUSB`

---

**Note**: Always ensure proper electrical safety when working with load control systems. Verify all connections and configurations before applying to live electrical loads.