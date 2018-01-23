import serial
import time
import DSWebClient
import Pilot
from serial.tools import list_ports

def getTime():
    return int(round(time.time() * 1000))
def sendFlashbang():
    port = 13246
    ip = "10.0.0.10"
    DSWebClient.sendTempAnimation(ip,port,"bluebang")

def main():
    print(serial.tools.list_ports)
    while(True):
        try:
            arduinoCom = next(list_ports.grep("rduino"))
            print("arduino port: "+str(arduinoCom.device))
            ser = serial.Serial(str(arduinoCom.device))  # open serial port
            print(ser.name)         # check which port was really used
            pilots = []
            pilots.append(Pilot.pilot("Sky"),0)
            pilots.append(Pilot.pilot("Ninja"),1)
            pilots.append(Pilot.pilot("PoisonPilot"),2)
            pilots.append(Pilot.pilot("Freefall"),3)
            for pilot in pilots:
                pilot.startLap()
            thresh = 140
            resetValue = 40
            readyForLap = True
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
                            lapTime = getTime()-lastTime
                            if((rssi>thresh)&(readyForLap)):
                                pilots[i].endLap()
                                pilots[i].startLap()
                                readyForLap = False
                                print("lap "+str(laps)+": "+str(lapTime/1000.0))
                                lastTime = getTime()
                                sendFlashbang()
                            if((not readyForLap)&(rssi<resetValue)&(lapTime>3000)):
                                readyForLap = True
                                print("reset")
                            lastFrame = getTime()
                    except Exception as e:
                        print(e)
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
