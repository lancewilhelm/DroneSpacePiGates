import serial
import time
import DSWebClient
import Pilot
import traceback
import logging
from serial.tools import list_ports

logging.basicConfig(filename="../../timing.log",level=logging.DEBUG)
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
    ip = ""
    DSWebClient.sendTempAnimation(ip,port,animation)

def main():
    print(serial.tools.list_ports)
    DSWebClient.sendTempAnimation("",13246,"flashbang")
    while(True):
        try:
            #arduinoCom = next(list_ports.grep("rduino"))
            arduinoCom = "/dev/ttyUSB0"
            #arduinoCom = "/dev/ttyACM0"
            #arduinoCom = "COM11"
            #print("arduino port: "+str(arduinoCom.device))
            #ser = serial.Serial(str(arduinoCom.device))  # open serial port
            ser = serial.Serial(arduinoCom,115200)
            #print(ser.name)         # check which port was really used
            pilots = []
            pilots.append(Pilot.pilot("Sky",0,"bluebang"))
            pilots.append(Pilot.pilot("ScraggleFPV",1,"greenbang"))
            pilots.append(Pilot.pilot("RandoBando",2,"flashbang"))
            pilots.append(Pilot.pilot("Ninja",3,"redbang"))
            try:
                while(True):
                    try:
                        line = ser.readline()
                        event = eval(line)
                        #print(event)
                        pilotId = event[0]
                        pilot = pilots[pilotId]
                        state = event[1]
                        timestamp = event[2]
                        if(state==PASS):
                            pilot.addLap(0,timestamp)
                            sendAnimation(pilot.getAnimation())
                            print(str(pilot.name)+": "+str(timestamp))
                            logging.debug(str(pilot.name)+": "+str(timestamp))
                        if(state==CALIBRATE):
                            print("calibrating module "+str(pilotId))
                        if(state==STANDBY):
                            print("module "+str(pilotId)+" ready")
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
