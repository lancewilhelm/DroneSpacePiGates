import serial
import time
def getTime():
    return int(round(time.time() * 1000))
#print(serial.tools.list_ports)
ser = serial.Serial('/dev/cu.usbmodem1411')  # open serial port
print(ser.name)         # check which port was really used
laps = 0
thresh = 230
resetValue = 210
readyForLap = True
lastTime = getTime()

try:
    while(True):
        try:
            line = ser.readline()
            print(line)
            #values = eval(line)
            #average = 0
            #for value in values:
            #    average+=value
            #average/=len(values)
            ##print(average)
            #if((average>thresh)&(readyForLap)):
            #    laps+=1
            #    readyForLap = False
            #    lapTime = getTime()-lastTime
            #    print("lap "+str(laps)+": "+str(lapTime/1000.0))
            #    lastTime = getTime()
            #if((not readyForLap)&(average<resetValue)):
            #    readyForLap = True
            #    print("reset")
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
          # close port
