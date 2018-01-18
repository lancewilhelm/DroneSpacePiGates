import serial
import time
import DSWebClient
from serial.tools import list_ports

def getTime():
    return int(round(time.time() * 1000))
def main():
    #print(serial.tools.list_ports)
    try:
        arduinoCom = next(list_ports.grep("rduino"))
        print("arduino port: "+arduinoCom)
        ser = serial.Serial(arduinoCom)  # open serial port
        print(ser.name)         # check which port was really used
        laps = 0
        thresh = 150
        resetValue = 70
        readyForLap = True
        lastTime = getTime()
        lastPing = lastTime
        lastFrame = lastTime
        try:
            while(True):
                try:
                    line = ser.readline()
                    values = eval(line)
                    average = values
                    #print(line)
                    #if ((lastFrame-lastPing) > 10000):
                    #    average = thresh+1
                    #    lastPing = lastFrame

                    print(line)
                    if((average>thresh)&(readyForLap)):
                        laps+=1
                        readyForLap = False
                        lapTime = getTime()-lastTime
                        print("lap "+str(laps)+": "+str(lapTime/1000.0))
                        lastTime = getTime()
                        DSWebClient.sendTempAnimation("",13246,"flashbang")
                    if((not readyForLap)&(average<resetValue)):
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
    except:
        print("arduino not found. Retrying...")
        time.sleep(5)
              # close port
main()
