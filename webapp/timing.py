import serial
import time
import DSWebClient
import Pilot
import traceback
from serial.tools import list_ports

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
            for pilot in pilots:
                pilot.startLap()
            thresh = 140
            resetValue = 40
            lastTime = getTime()
            lastPing = lastTime
            lastFrame = lastTime
            try:
                while(True):
                    try:
                        line = ser.readline()
                        values = eval(line)
                        print(values)
                        for i in range(0,len(values)):
                            rssi = values[i]
                            pilot = pilots[i]
                            lapTime = getTime()-lastTime
                            if((rssi>thresh)&(pilot.readyForLap)):
                                pilot.endLap()
                                pilot.startLap()
                                pilot.readyForLap = False
                                print("lap "+str(len(pilot.laps))+": "+str(lapTime/1000.0))
                                sendAnimation(pilot.getAnimation())
                            if((not pilot.readyForLap)&(rssi<resetValue)&(lapTime>3000)):
                                pilot.readyForLap = True
                                print("reset")
                            lastFrame = getTime()
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
