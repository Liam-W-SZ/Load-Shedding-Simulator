# Load Shedding Simulator and Load Sequencer

This repository contains two main projects: **Load Shedding Simulator** and **Load Sequencer Simulator**, both designed to manage and simulate electrical load control using Python. These tools are primarily used for testing and managing load shedding schedules and sequences.

---

## Table of Contents
- [Load Shedding Simulator](#load-shedding-simulator)
  - [Overview](#overview)
  - [Features](#features)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [Dependencies](#dependencies)
- [Load Sequencer Simulator](#load-sequencer-simulator)
  - [Overview](#overview-1)
  - [Features](#features-1)
  - [Usage](#usage-1)
  - [Configuration](#configuration-1)
  - [Troubleshooting](#troubleshooting)
- [Folder Structure](#folder-structure)

---

## Load Shedding Simulator

### Overview
The **Load Shedding Simulator (LSS)** is a Python-based GUI application that simulates load shedding schedules. It allows users to configure predefined or custom load shedding schedules and provides manual control over grid and load states.

### Features
- **Predefined Schedules**: Select from predefined load shedding stages (e.g., Stage 1 to Stage 8).
- **Custom Simulations**: Define custom schedules with specific on/off durations for essential and non-essential loads.
- **Manual Controls**: Manually toggle grid, essential, and non-essential loads.
- **Status Panel**: Displays real-time simulation status, including timers and messages.
- **Graceful Shutdown**: Ensures all loads are turned off when the simulation ends.

### Usage
1. **Run the Simulator**:
   - Activate the virtual environment:
     ```bash
     source ~/myenv/bin/activate
     ```
   - Run the main script:
     ```bash
     python V4.py
     ```
2. **Select a Schedule**:
   - Use the dropdown menu to choose a predefined or custom schedule.
3. **Start/Stop Simulation**:
   - Click "Start Sim" to begin the simulation.
   - Click "End Sim" to stop the simulation.

### Configuration
- **Load Shedding Config File**:
  - Located at `Eng_Model_Code_2025/Load_Shedding_Config_File.json`.
  - Defines predefined schedules (e.g., Stage 1 to Stage 8) and custom simulation parameters.

### Dependencies
- Python 3.x
- Libraries:
  - `tkinter`
  - `Pillow`
  - `minimalmodbus`
  - `numpy`

---

## Load Sequencer Simulator

### Overview
The **Load Sequencer Simulator** is a Python-based tool for controlling electrical loads via Modbus RTU communication. It supports two operation modes: **Periodic** and **Sequence**.

### Features
- **Periodic Mode**: Controls meters with duty cycles (percentage on-time over a period).
- **Sequence Mode**: Executes time-based meter control with scheduled state changes.
- **Real-time Monitoring**: Displays current status and next scheduled actions.
- **Multiple Sets**: Supports multiple meter groups running in separate threads.

### Usage
1. **Run the Simulator**:
   - Activate the virtual environment:
     ```bash
     source .venv/bin/activate
     ```
   - Run the simulator:
     ```bash
     python simulator.py --mode periodic
     python simulator.py --mode sequence
     ```
2. **Periodic Mode**:
   - Select a configuration file from the `Periodics/` folder.
   - Meters cycle between ON/OFF based on duty cycle and period.
3. **Sequence Mode**:
   - Select a configuration file from the `Sequenced/` folder.
   - Executes actions at scheduled times.

### Configuration
- **Meter Configuration**:
  - Located at `Load Sequencer/Configs/meter_config.json`.
  - Defines meter addresses for Modbus communication.
- **JSON Templates**:
  - Periodic tests: `Load Sequencer/Periodics/`.
  - Sequence tests: `Load Sequencer/Sequenced/`.

### Troubleshooting
- **Common Issues**:
  - Missing JSON files: Ensure files are in the correct folders.
  - Meter not found: Verify meter names in `meter_config.json`.
  - Communication errors: Check USB-to-RS485 adapter and Modbus device connections.

---

## Folder Structure

```
Eng_Model_Code_2025/
├── Help_File.txt
├── Image_Test.py
├── Load_Shedding_Config_File.json
├── Main_ModBus_Script.py
├── Old_Python_Scripts/
│   ├── V2.py
│   ├── V3.py
│   └── V4_before_Scheduling_Updates.py
├── V4.py
├── run.sh
└── Load Shedding Lengths Specs.txt

Load Sequencer/
├── Configs/
│   └── meter_config.json
├── Periodics/
│   ├── grid_test.json
│   └── periodic_test.json
├── Sequenced/
│   ├── sequence_test.json
│   └── sequence_test_carl.json
├── readme.txt
├── requirements.txt
├── simulator.py
└── tv_tools.py
```

---

For further assistance, refer to the `Help_File.txt` or contact the development team.
