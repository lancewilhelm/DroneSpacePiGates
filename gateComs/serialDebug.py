import os
import sys
import traceback
class Arduino:
    def __init__(self):
        self.serial = None
        self.connected = False
    def connect(self):
        print("connecting arduino")
        try:
            #arduinoCom = next(list_ports.grep("rduino"))

            arduinoCom = "/dev/ttyUSB0"
            #arduinoCom = "/dev/ttyACM0"
            #arduinoCom = "COM11"
            #print("arduino port: "+str(arduinoCom.device))
            #ser = serial.Serial(str(arduinoCom.device))  # open serial port
            self.serial = serial.Serial(arduinoCom,115200, timeout=0.02)
            #print(ser.name)         # check which port was really used
            self.clearPilotData()
            print("arduino connected")
            return True
        except Exception as e:
            print("failed to connect to arduino ")
            print(traceback.format_exc())
            print("failed to connect arduino")
            print(e)
            return False

    def disconnect(self):
        print("disconnecting arduino")
        try:
            self.serial.close()
        except Exception as e:
            print(e)
        self.connected = False

    def printSerial(self):
        try:
            if self.connected:
                line = self.serial.readline()
                print(line)
        except Exception as e:
            print(traceback.format_exc())

    def isConnected(self):
        return self.connected

def main():
    arduino = Arduino()
    arduino.connect()
    while(arduino.isConnected()):
        arduino.printSerial()
    arduino.disconnect()
    print("program done")

main()
