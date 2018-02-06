import serial
import time
import DSWebClient
import Pilot
import traceback
from serial.tools import list_ports

#these are the states we'll use to let our loop know what a given RX is doing atm
CALIBRATE = 0;    #the moments while a module is discovering its noise floor
STANDBY = 1;      #the moments before a race starts
START = 2;        #the moment when the race starts
FAR = 3;          #the moments while a quad is out of the bubble
ENTER = 4;        #the moments while quad passes through the bubble
PASS = 5;         #the moment an rssi peaks inside the bubble
EXIT = 6;         #the moment when a quad exits the bubble
CHANNEL_HOP = 9;  #the moments while a module stablizes after a channel change. this should only happen when a quad is out of the bubble
FINISHED = 10;    #the moment when the race is completed

def getTime():
    return int(round(time.time() * 1000))
def sendAnimation(animation):
    port = 13246
    ip = "10.0.0.10"
    DSWebClient.sendTempAnimation(ip,port,animation)

def main():
    print(serial.tools.list_ports)
    while(True):
        try:
            #arduinoCom = next(list_ports.grep("rduino"))
            arduinoCom = "/dev/ttyUSB0"
            #arduinoCom = "/dev/ttyACM0"
            #print("arduino port: "+str(arduinoCom.device))
            #ser = serial.Serial(str(arduinoCom.device))  # open serial port
            ser = serial.Serial(arduinoCom,115200)
            #print(ser.name)         # check which port was really used
            pilots = []
            pilots.append(Pilot.pilot("Sky",0,"bluebang"))
            pilots.append(Pilot.pilot("Ninja",1,"redbang"))
            pilots.append(Pilot.pilot("PoisonPilot",2,"greenbang"))
            pilots.append(Pilot.pilot("Freefall",3,"flashbang"))
            try:
                while(True):
                    try:
                        line = ser.readline()
                        event = eval(line)
                        print(event)
                        pilotId = event[0]
                        state = event[1]
                        timestamp = event[2]
                        if(state==PASS):
                            addLap(0,timestamp)
                            sendAnimation(pilots[pilotId].getAnimation())
                    except Exception as e:
                        print(traceback.format_exc())
                        print("bad data: "+str(line))
                        ser.close()
                        time.sleep(10)
                        try:
                            ser = serial.Serial('/dev/cu.usbmodem1421')
                        except:
                            pass
            except KeyboardInterrupt:
                ser.close()
                raise
                quit()
        except Exception as e:
            print(e)
            print("arduino not found. Retrying...")
            time.sleep(5)
              # close port
main()
