import minimalmodbus #an easy-to-use Python module for talking to instruments (slaves) from a computer (master) using the Modbus protocol (For the USB to RS485 dongal)
# Note we had to break the pi to install this  library

import os #interact with operating system
import time   #retrieving the current time, waiting during code execution, and measuring the efficiency of your code
import serial #connect to COM port to send and receive data
import serial.tools.list_ports


Grid_Address = 4 # Modbus address of IVY for Grid


ESS_Address = 8 # Modbus address of IVY for Load (Essential)
Non_ESS_Address = 5 # Modbus address of IVY for Load (Non - Essential)

#Carl
ESS_Address2 = 9
Non_ESS_Address2 = 6


# ESS_Address = 5 # Modbus address of IVY for Load (Essential)
# Non_ESS_Address = 8 # Modbus address of IVY for Load (Non - Essential)

# #Carl
# ESS_Address2 = 6
# Non_ESS_Address2 = 9

E4_Address = 16
init = False
sleeptime = 0.08



instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 16, debug = False) # 'instrument' object (port name, E4 address, )
instrument.serial.stopbits = 1  # Number of stop bits
instrument.mode = minimalmodbus.MODE_RTU # Mode to be used (RTU or ASCII)
instrument.serial.timeout = 0.07   # Timeout time in seconds
instrument.serial.baudrate = 9600     # BaudRate
instrument.serial.parity = serial.PARITY_NONE  # Number of data bits to be requested
instrument.handle_local_echo = False
init = True
os.system('cls')


def GridOn():
      
      instrument.address = Grid_Address
      instrument.serial.timeout = 0.07
      instrument.write_register(4096, 0xff00)
      print('Grid On')
      #entry_1.insert("1,0","Grid On button pressed \n")

def GridOff():
        instrument.address = Grid_Address
        instrument.serial.timeout = 0.07
        instrument.write_register(4096, 0)   
        print('Grid Off')
        #gui.entry_1.insert("1,0","Grid Off button pressed \n")

def EssLoadOn():
        
        try:                
                instrument.address = ESS_Address
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0xff00)
                print('Ess Load 1 on')
              
        except:
                print('No Coms to put Ess load on')

def EssLoadOff():
        
        try:
                instrument.address = ESS_Address
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0)
                print('Ess Load 1 Off')
        except:
                print('No Coms to put Ess load off')

def NessLoadOn():
        
        try:                
                instrument.address = Non_ESS_Address
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0xff00)
                print('Ness Load 1 on')
              
        except:
                print('No Coms to put Ness load on')

def NessLoadOff():
        
        try:
                instrument.address = Non_ESS_Address
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0)
                print('Ness Load 1 Off')
        except:
                print('No Coms to put Ness load off')

#second set of functions for Carl's IVY
def EssLoadOn2():
        
        try:                
                instrument.address = ESS_Address2
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0xff00)
                print('Ess Load 2 on')
              
        except:
                print('No Coms to put Ess load 2 on')

def EssLoadOff2():
        
        try:
                instrument.address = ESS_Address2
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0)
                print('Ess Load 2 Off')
        except:
                print('No Coms to put Ess load 2 off')

def NessLoadOn2():
        
        try:                
                instrument.address = Non_ESS_Address2
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0xff00)
                print('Ness Load 2 on')
              
        except:
                print('No Coms to put Ness load 2 on')

def NessLoadOff2():
        
        try:
                instrument.address = Non_ESS_Address2
                instrument.serial.timeout = 0.07
                instrument.write_register(4096, 0)
                print('Ness Load 2 Off')
        except:
                print('No Coms to put Ness load 2 off')


def Relay_Toggle_Non_ESS(target_state : bool):
        
        relay_cmd = 0xff00 if target_state == True else 0
        success = False
        try:
                instrument.address = Non_ESS_Address
                instrument.serial.timeout = 0.15
                instrument.write_register(4096, relay_cmd)
                success = True
        except:
                print('No Coms to toggle Ness load')
        
        if not success:
                time.sleep(0.15)
                try:
                        instrument.address = Non_ESS_Address
                        instrument.serial.timeout = 0.15
                        instrument.write_register(4096, relay_cmd)
                        success = True
                except:
                        print('No Coms to toggle Ness load')

def Relay_Toggle_Non_ESS2(target_state : bool):
        
        relay_cmd = 0xff00 if target_state == True else 0
        success = False
        try:
                instrument.address = Non_ESS_Address2
                instrument.serial.timeout = 0.15
                instrument.write_register(4096, relay_cmd)
                success = True
        except:
                print('No Coms to toggle Ness load')
        
        if not success:
                time.sleep(0.15)
                try:
                        instrument.address = Non_ESS_Address2
                        instrument.serial.timeout = 0.15
                        instrument.write_register(4096, relay_cmd)
                        success = True
                except:
                        print('No Coms to toggle Ness load')

def Relay_Toggle_ESS2(target_state : bool):
        
        relay_cmd = 0xff00 if target_state == True else 0
        success = False
        try:
                instrument.address = ESS_Address2
                instrument.serial.timeout = 0.15
                instrument.write_register(4096, relay_cmd)
                success = True
        except:
                print('No Coms to toggle Ness load')
        
        if not success:
                time.sleep(0.15)
                try:
                        instrument.address = ESS_Address2
                        instrument.serial.timeout = 0.15
                        instrument.write_register(4096, relay_cmd)
                        success = True
                except:
                        print('No Coms to toggle Ness load')

def Relay_Toggle_ESS(target_state : bool):
        
        relay_cmd = 0xff00 if target_state == True else 0
        success = False
        try:
                instrument.address = ESS_Address
                instrument.serial.timeout = 0.15
                instrument.write_register(4096, relay_cmd)
                success = True
        except:
                print('No Coms to toggle Ness load')
        
        if not success:
                time.sleep(0.15)
                try:
                        instrument.address = ESS_Address
                        instrument.serial.timeout = 0.15
                        instrument.write_register(4096, relay_cmd)
                        success = True
                except:
                        print('No Coms to toggle Ness load')