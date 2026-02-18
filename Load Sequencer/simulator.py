#!/usr/bin/env python3
# filepath: /home/mca-atp-1/Desktop/Load Sequencer/simulator.py

import argparse
import json
import threading
import time
import signal
import sys
import os
from datetime import datetime
from tv_tools import get_modbus_instruments, toggle_Meter, close_modbus_connections

def list_config_files(folder_path):
    """List all JSON files in the specified folder"""
    try:
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' does not exist.")
            return []
        
        files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
        return sorted(files)
    except Exception as e:
        print(f"Error listing files in {folder_path}: {e}")
        return []

def select_config_file(folder_path, test_type):
    """Allow user to select a configuration file from the folder"""
    files = list_config_files(folder_path)
    
    if not files:
        print(f"No JSON configuration files found in '{folder_path}' folder.")
        sys.exit(1)
    
    print(f"\nAvailable {test_type} configuration files:")
    print("-" * 50)
    for i, filename in enumerate(files, 1):
        print(f"{i}. {filename}")
    
    while True:
        try:
            choice = input(f"\nSelect a {test_type} configuration file (1-{len(files)}): ")
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(files):
                selected_file = files[choice_num - 1]
                file_path = os.path.join(folder_path, selected_file)
                print(f"Selected: {selected_file}")
                return file_path
            else:
                print(f"Please enter a number between 1 and {len(files)}")
                
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)

class PeriodicController:
    def __init__(self, config_file):
        self.config_file = config_file
        self.running = False
        self.threads = []
        self.meters = {}
        self.meter_config = {}
        self.load_config()
        self.load_meter_config()
        
    def load_config(self):
        """Load the periodic test configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            print(f"Loaded configuration: {self.config['Description']} v{self.config['Version']}")
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    def load_meter_config(self):
        """Load meter addresses from meter_config.json file"""
        try:
            with open('Configs/meter_config.json', 'r') as f:
                self.meter_config = json.load(f)
            print(f"Loaded meter configuration with {len(self.meter_config)} meters")
        except Exception as e:
            print(f"Error loading meter config file: {e}")
            sys.exit(1)
    
    def initialize_meters(self):
        """Initialize all meters based on meter_config.json"""
        for meter_name, address in self.meter_config.items():
            try:
                meter = get_modbus_instruments(address)
                if meter:
                    self.meters[meter_name] = meter
                    print(f"Initialized meter: {meter_name} at address {address}")
                else:
                    print(f"Failed to initialize meter: {meter_name} at address {address}")
            except Exception as e:
                print(f"Error initializing meter {meter_name}: {e}")
    
    def initialize_meter_on_demand(self, meter_name):
        """Initialize a specific meter when needed"""
        if meter_name in self.meters:
            return True  # Already initialized
        
        try:
            # Get address from meter_config.json
            if meter_name in self.meter_config:
                address = self.meter_config[meter_name]
                meter = get_modbus_instruments(address)
                if meter:
                    self.meters[meter_name] = meter
                    print(f"Initialized meter on demand: {meter_name} at address {address}")
                    return True
                else:
                    print(f"Failed to initialize meter: {meter_name} at address {address}")
                    return False
            else:
                print(f"Meter {meter_name} not found in meter_config.json")
                return False
        except Exception as e:
            print(f"Error initializing meter {meter_name}: {e}")
            return False

    def run_set_thread(self, set_name, set_config):
        """Run a single set in its own thread"""
        print(f"Starting thread for set: {set_name}")
        print(f"DEBUG: set_config.items() = {list(set_config.items())}")
        
        while self.running:
            for meter_name, params in set_config.items():
                if not self.running:
                    break
                    
                duty = params['Duty']  # Percentage
                period = params['Period']  # Minutes
                
                on_time = (period * 60) * (duty / 100)  # Convert to seconds
                off_time = (period * 60) - on_time
                
                # Initialize meter on demand
                if self.initialize_meter_on_demand(meter_name):
                    try:
                        # Turn meter ON
                        toggle_Meter(self.meters[meter_name], True)
                        print(f"[{set_name}] {meter_name} ON for {on_time:.1f}s")
                        time.sleep(on_time)
                        
                        if not self.running:
                            break
                            
                        # Turn meter OFF
                        toggle_Meter(self.meters[meter_name], False)
                        print(f"[{set_name}] {meter_name} OFF for {off_time:.1f}s")
                        time.sleep(off_time)
                        
                    except Exception as e:
                        print(f"Error controlling meter {meter_name}: {e}")
                else:
                    print(f"Could not initialize meter {meter_name}")

    def start_periodic(self):
        """Start periodic mode - run all sets in separate threads"""
        self.running = True
        
        sets = self.config.get("Sets", {})
        
        for set_name, set_config in sets.items():
            thread = threading.Thread(
                target=self.run_set_thread,
                args=(set_name, set_config),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        print(f"Started {len(self.threads)} threads for periodic testing")
        print("Press Ctrl+C to stop...")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop all threads and cleanup"""
        print("\nStopping periodic controller...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=1)
        
        # Close modbus connections
        for meter_name, meter in self.meters.items():
            try:
                close_modbus_connections(meter)
                print(f"Closed connection to {meter_name}")
            except Exception as e:
                print(f"Error closing {meter_name}: {e}")
        
        print("Cleanup complete")

class SequenceController:
    def __init__(self, config_file):
        self.config_file = config_file
        self.running = False
        self.meters = {}
        self.meter_config = {}
        self.load_config()
        self.load_meter_config()
        
    def load_config(self):
        """Load the sequence test configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            print(f"Loaded configuration: {self.config['Description']} v{self.config['Version']}")
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    def load_meter_config(self):
        """Load meter addresses from meter_config.json file"""
        try:
            with open('Configs/meter_config.json', 'r') as f:
                self.meter_config = json.load(f)
            print(f"Loaded meter configuration with {len(self.meter_config)} meters")
        except Exception as e:
            print(f"Error loading meter config file: {e}")
            sys.exit(1)
    
    def initialize_meter_on_demand(self, meter_name):
        """Initialize a specific meter when needed"""
        if meter_name in self.meters:
            return True  # Already initialized
        
        try:
            # Get address from meter_config.json
            if meter_name in self.meter_config:
                address = self.meter_config[meter_name]
                meter = get_modbus_instruments(address)
                if meter:
                    self.meters[meter_name] = meter
                    print(f"Initialized meter on demand: {meter_name} at address {address}")
                    return True
                else:
                    print(f"Failed to initialize meter: {meter_name} at address {address}")
                    return False
            else:
                print(f"Meter {meter_name} not found in meter_config.json")
                return False
        except Exception as e:
            print(f"Error initializing meter {meter_name}: {e}")
            return False
    
    def start_sequence(self):
        """Start sequence test mode"""
        print("Starting sequence test mode...")
        self.running = True
        
        sequence = self.config.get("Sequence", {})
        
        # Get current time and find the last executed timestamp
        current_time = datetime.now().strftime("%H:%M")
        last_executed_time = self.find_last_timestamp_before_current(sequence, current_time)
        
        # Initialize meters based on the last timestamp before current time
        if last_executed_time:
            print(f"\nInitializing meters based on last timestamp: {last_executed_time}")
            actions = sequence[last_executed_time]
            for meter_name, state in actions.items():
                if self.initialize_meter_on_demand(meter_name):
                    try:
                        meter_state = state.lower() in ['on', 'true', '1']
                        result = toggle_Meter(self.meters[meter_name], meter_state)
                        print(f"  {meter_name}: {state} ({meter_state}) - {result}")
                    except Exception as e:
                        print(f"  Error controlling meter {meter_name}: {e}")
                else:
                    print(f"  Could not initialize meter {meter_name}")
        else:
            print("No previous timestamp found, meters remain in default state")
        
        # Display next state change time
        next_timestamp = self.find_next_timestamp_after_current(sequence, current_time)
        if next_timestamp:
            print(f"\nNext state change scheduled for: {next_timestamp}")
        else:
            print("\nNo upcoming state changes scheduled for today")
        
        print("Sequence test running. Checking time every 30 seconds...")
        print("Press Ctrl+C to stop...")
        
        while self.running:
            time.sleep(30)
            try:
                current_time = datetime.now().strftime("%H:%M")
                
                if current_time in sequence and current_time != last_executed_time:
                    print(f"\n[{current_time}] Executing sequence actions...")
                    
                    actions = sequence[current_time]
                    for meter_name, state in actions.items():
                        if self.initialize_meter_on_demand(meter_name):
                            try:
                                meter_state = state.lower() in ['on', 'true', '1']
                                result = toggle_Meter(self.meters[meter_name], meter_state)
                                print(f"  {meter_name}: {state} ({meter_state}) - {result}")
                            except Exception as e:
                                print(f"  Error controlling meter {meter_name}: {e}")
                        else:
                            print(f"  Could not initialize meter {meter_name}")
                    
                    last_executed_time = current_time
                    print(f"Sequence for {current_time} completed.")
                    
                    # Display next state change time
                    next_timestamp = self.find_next_timestamp_after_current(sequence, current_time)
                    if next_timestamp:
                        print(f"Next state change scheduled for: {next_timestamp}\n")
                    else:
                        print("No more state changes scheduled for today\n")
            

            
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                print(f"Error in sequence test: {e}")
                time.sleep(30)

    def find_last_timestamp_before_current(self, sequence, current_time):
        """Find the last timestamp in sequence that comes before current time"""
        # Convert time strings to comparable format (minutes since midnight)
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        current_minutes = time_to_minutes(current_time)
        last_timestamp = None
        last_minutes = -1
        
        for timestamp in sequence.keys():
            timestamp_minutes = time_to_minutes(timestamp)
            if timestamp_minutes <= current_minutes and timestamp_minutes > last_minutes:
                last_minutes = timestamp_minutes
                last_timestamp = timestamp
        
        return last_timestamp

    def find_next_timestamp_after_current(self, sequence, current_time):
        """Find the next timestamp in sequence that comes after current time"""
        # Convert time strings to comparable format (minutes since midnight)
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        current_minutes = time_to_minutes(current_time)
        next_timestamp = None
        next_minutes = 24 * 60  # End of day
        
        for timestamp in sequence.keys():
            timestamp_minutes = time_to_minutes(timestamp)
            if timestamp_minutes > current_minutes and timestamp_minutes < next_minutes:
                next_minutes = timestamp_minutes
                next_timestamp = timestamp
        
        return next_timestamp

def signal_handler(sig, frame, controller):
    """Handle Ctrl+C gracefully"""
    controller.stop()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Load Sequencer Simulator')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--periodic', action='store_true', 
                      help='Run periodic test mode')
    group.add_argument('-s', '--sequence', action='store_true', 
                      help='Run sequence test mode')
    
    args = parser.parse_args()
    
    if args.periodic:
        # Select periodic configuration file
        config_file = select_config_file('Periodics', 'periodic')
        controller = PeriodicController(config_file)
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, controller))
        
        controller.start_periodic()
        
    elif args.sequence:
        # Select sequence configuration file
        config_file = select_config_file('Sequenced', 'sequence')
        controller = SequenceController(config_file)
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, controller))
        
        controller.start_sequence()

if __name__ == "__main__":
    main()