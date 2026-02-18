import jsonpickle
import ftplib
import os
import glob
import minimalmodbus
import serial




class root:
  def __init__(self, ts, tester, testdesc, testjig, deviceid, prefix, jobnr, szserialnr, procedure, productGroup, supplierserial, lowerlevelID, tests, errors, result):
    self.ts = ts            
    self.tester = tester      
    self.testdesc = testdesc
    self.testjig = testjig
    self.deviceid = deviceid
    self.prefix = prefix
    self.jobnr = jobnr
    self.szserialnr = szserialnr
    self.procedure = procedure
    self.productGroup = productGroup
    self.supplierserial = supplierserial
    self.lowerlevelID = lowerlevelID
    self.tests = tests #list of tests
    self.errors = errors
    self.result = result
   
def testResultReset (root):
    root.ts = ""            
    root.tester = root.tester      
    root.testdesc = ""
    root.testjig = ""
    root.deviceid = ""
    root.jobnr = ""
    root.szserialnr = ""
    root.procedure = "FTP"
    root.supplierserial = ""
    root.lowerlevelID = ""
    root.tests = []
    root.result = ""
    return root

class test:
  def __init__(self, description, expected, received, result, test_type, test_range, required):
    self.description = description
    self.expected = expected
    self.received = received
    self.result = result
    self.test_type = test_type
    self.test_range = test_range
    self.required = required
    
class Device:
  def __init__(self, product, szs, deviceName, tbDeviceID, tbDeviceLabel, sessionJWT):
    self.product = product
    self.szs = szs
    self.deviceName = deviceName
    self.tbDeviceID = tbDeviceID
    self.tbDeviceLabel = tbDeviceLabel
    self.sessionJWT = sessionJWT

def outputJSON(root, ftpfolder):
    s = jsonpickle.encode(root, unpicklable = False)
    filename= root.deviceid + "_"+ root.jobnr+"_"+str(root.ts)+".json"
    filepath = os.getcwd() +"/results/" + filename
    f = open(filepath, "x")
    f.write(s)
    f.close()
    session = ftplib.FTP_TLS('13.246.31.38')
    session.login('ftpuser','ftpuser')
    session.prot_p()
    session.cwd(ftpfolder)
    file = open(filepath,'rb')                  # file to send
    session.storbinary('STOR ' + filename, file)     # send the file
    file.close()                                    # close file and FTP
    session.quit()
    return s
def list_serial_ports():
    """List all available serial ports"""
    import glob
    ports = glob.glob('/dev/tty[A-Za-z]*')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
def modbus_Init(address=1, port='/dev/ttyUSB0'):
    """Initialize Modbus RTU connection for multiple devices on RS485 bus"""
    #print(f"modbus_Init: Trying to comms to address: {address}")
    try:
        # List available ports
        available_ports = list_serial_ports()
        #print(f"Available serial ports: {available_ports}")
        
        if port not in available_ports:
            raise Exception(f"Port {port} not found. Available ports: {available_ports}")
            
        # Create and configure Modbus instrument
        instrument = minimalmodbus.Instrument(
            port=port,
            slaveaddress=address,
            debug=False  # Enable debug mode temporarily
        )
        
        instrument.serial.baudrate = 9600
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1.0
        
        # Modbus mode configuration
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.clear_buffers_before_each_transaction = True
        instrument.handle_local_echo = False
        try:
            instrument.read_register(305, 0, 3)
            #print(f"Successfully connected to device at address {address}")
        except Exception as e:
            print(f"Communication test failed: {e}")
            raise
            
        return instrument
        
    except Exception as e:
        print(f"Modbus initialization error: {e}")
        return None
def get_modbus_instruments(address):
    #print(f"get_modbus_instruments: Enter with address {address}")
    """Get Modbus instrument for the specified address"""
    try:
        instrument = modbus_Init(address=address)
        return instrument
    except Exception as e:
        print(f"Error initializing modbus instrument at address {address}: {e}")
        return None
def close_modbus_connections(instrument):
    """Close all Modbus connections"""
    #print(f"close_modbus_connections: Intrument Found")
    if instrument and instrument.serial.is_open:
        #print(f"close_modbus_connections: closing")
        instrument.serial.close()



def toggle_Meter(meter, state):
    """
    Toggle a specific meter's state if different from desired state
    
    Args:
        meter: Modbus instrument object (not address)
        state (bool): Desired state (True for On, False for Off)
        
    Returns:
        str: Result message indicating what happened
    """
    result = ""
    try:
        if meter is None:
            raise Exception("Modbus instrument not found")
            
        try:
            if state:  # state is boolean: True = On, False = Off
                meter.write_register(4096, 0xff00)  # Using function code 6
                result = f"Meter switched to On"
            else:
                meter.write_register(4096, 0)  # Using function code 6
                result = f"Meter switched to Off"
        except Exception as write_error:
            raise Exception(f"Write failed: {write_error}")
            
    except Exception as e:
        result = f"Error toggling meter: {e}"
            
    return result
