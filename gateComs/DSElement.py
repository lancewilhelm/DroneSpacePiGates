import socket
import time
import select
import time
import DSUtils
import os
import sys
import logging
import traceback
import argparse
import psutil

import serial
import Pilot
from serial.tools import list_ports

try:
    import LEDUtils
except ImportError:
    pass


try:
    import cPickle as pickle
except:
    import pickle

CALIBRATE = 0    #the moments while a module is discovering its noise floor
STANDBY = 1      #the moments before a race starts
START = 2        #the moment when the race starts
FAR = 3          #the moments while a quad is out of the bubble
ENTER = 4        #the moments while quad passes through the bubble
PASS = 5         #the moment an rssi peaks inside the bubble
EXIT = 6         #the moment when a quad exits the bubble
RSSI_UPDATE = 7
CHANNEL_HOP = 9  #the moments while a module stablizes after a channel change. this should only happen when a quad is out of the bubble
FINISHED = 10    #the moment when the race is completed

def sendAnimation(animation):
    port = 13247
    ip = ""
    DSWebClient.sendTempAnimation(ip,port,animation)

class gate:
    def __init__(self,args):
        self.args = args

    def start(self):
        element(self.args).start()

class pillar:
    def __init__(self,args):
        self.args = args

    def start(self):
        element(self.args).start()

class element:
    def __init__(self,args):
        self.devMode = args.d
        if(self.devMode==False): #if we are in dev mod, we won't load pi specific libraries
            print("we are not in dev mode")
        else:
            print("we are in dev mode")
        #lets handle the arguments for this element
        logLevel = logging.WARNING
        if(args.l=="off"):
            logLevel = logging.ERROR
        elif(args.l=="low"):
            logLevel = logging.WARNING
        elif(args.l=="medium"):
            logLevel = logging.DEBUG
        elif(args.l=="high"):
            logLevel = logging.INFO
        logFile = args.f
        logging.basicConfig(filename=logFile,level=logLevel)

        self.serverAddress = args.i
        self.port = args.p
        self.currentColor = args.c
        self.defaultColor = args.c
        self.ledCount = args.e
        self.lastUpdate = self.getTime() #Used for keeping track of when to send next keepalive
        self.keepaliveDelay = 5000 #keepalive delay in ms
        self.connectionTimeout = 15000 #time in ms of not being able to send before we consider the network disconnected
        self.tempAnimationQueue = []
        self.serial = None
        self.arduinoConnected = False
        self.pilots = []

    def getSendableLaps(self):
        laps = []
        for pilot in self.pilots:
            for lap in pilot.laps:
                laps.append([pilot.name,lap.duration,lap.number])
        return laps

    def clearLaps(self):
        self.clearPilotData()

    def clearPilotData(self):
        self.pilots = []
        self.pilots.append(Pilot.pilot("White",0,"bluebang",[0,0,1]))
        self.pilots.append(Pilot.pilot("Green",1,"redbang",[1,0,0]))
        self.pilots.append(Pilot.pilot("Red",2,"greenbang",[0,1,0]))
        self.pilots.append(Pilot.pilot("Blue",3,"tempFlashYellow",[0.5,0.5,0]))

    def connectArduino(self):
        print("connecting arduino")
        arduinoPorts = ["/dev/ttyUSB0","/dev/ttyACM0","/dev/ttyAMA0","/dev/tty.wchusbserial1420","/dev/tty.wchusbserial1410"]
        connected = False
        for arduinoCom in arduinoPorts:
            try:
                #arduinoCom = next(list_ports.grep("rduino"))

                #arduinoCom = "/dev/ttyACM0"
                #arduinoCom = "COM11"
                #print("arduino port: "+str(arduinoCom.device))
                #ser = serial.Serial(str(arduinoCom.device))  # open serial port
                self.serial = serial.Serial(arduinoCom,115200, timeout=0.02)
                #print(ser.name)         # check which port was really used
                self.clearPilotData()
                logging.debug("arduino connected")
                connected = True
                break

            except Exception as e:
                logging.debug("failed to connect to arduino on port "+arduinoCom)
                logging.debug(traceback.format_exc())
                logging.debug("failed to connect arduino")
                logging.debug(e)
                connected = False
        return connected

    def disconnectArduino(self):
        logging.debug("disconnecting arduino")
        try:
            self.serial.close()
        except Exception as e:
            logging.debug(e)
        self.arduinoConnected = False
    def writeSerial(self, data):
        if self.arduinoConnected == False:
            logging.debug("no arduino connected. Attempting to reconnect")
            self.arduinoConnected = self.connectArduino()
        if self.arduinoConnected == True:
            logging.debug("sending '"+data+"' to arduino")
            message = data + "/r/n"
            self.serial.write(message.encode())


    def readSerial(self):
        try:
            if self.arduinoConnected:
                line = self.serial.readline()
                try:
                    event = eval(line)
                except:
                    event = None
                if(event!=None):

                    pilotId = event[0]
                    pilot = self.pilots[pilotId]
                    state = event[1]
                    timestamp = event[2]
                    if(state!=RSSI_UPDATE):
                        logging.debug(line)
                    if(state==RSSI_UPDATE):
                        pilot.distance = timestamp
                    if(state==PASS):
                        pilot.addLap(0,timestamp)
                        logging.debug(str(pilot.name)+": "+str(timestamp))
                        logging.debug(str(pilot.name)+": "+str(timestamp))
                    if(state==ENTER):
                        self.tempAnimationQueue.append(pilot.animation)
                    if(state==CALIBRATE):
                        logging.debug("calibrating module "+str(pilotId))
                        self.tempAnimationQueue.append(pilot.animation)
                    if(state==STANDBY):
                        logging.debug("module "+str(pilotId)+" ready")
        except Exception as e:
            self.arduinoConnected = False
            logging.debug(e)
            logging.debug(traceback.format_exc())

    def createSocket(self,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.bind(('',13248))
        sock.setblocking(0)
        return sock

    def connectToServer(self,sock,address,LED):
        logging.debug("connecting to server at: "+str(address))
        self.sendData(sock,address,"connect","","")
        logging.debug("sent connection request to server")
        logging.debug("waiting for server to respond")
        #sock.setblocking(1) #freeze the program for up to 5 seconds until we get some data back
        #sock.settimeout(10)
        startTime = self.getTime()
        while(True):

            self.updateAnimations(LED)
            data,address = self.recvData(sock)
            if(data):
                connectionSuccess = self.handleMessage(sock,address,data,LED)
                break
            else:
                connectionSuccess = False
            if self.getTime()-startTime>10000:
                break
        if(connectionSuccess):
            logging.debug(self.currentColor)
            logging.debug("got connection response "+str(data))
        else:
            logging.debug("no response from server")
            #lets run our fallback animation
            self.handleMessage(sock,address,{"body":self.currentColor,"subject":"updateAnimation","recipient":""},LED)
            self.updateAnimations(LED) #make the animation actually play momentarily
        return connectionSuccess
    def recvData(self,sock): #this is where we handle all recieved data
        global currentColor
        data = None
        address = None
        try:
            data, address = sock.recvfrom(10240)
        except:
            pass
        if(data):
            try:
                data = pickle.loads(data)
                subject = data['subject'] #the subject of the message
                body = data['body'] #the body of the message
                recipient = data['recipient'] #the intended recipient of the massage. This may be blank. If so, it's for everyone
                #try:
                #    data = data.decode(encoding='utf-8')
                #except:
                #    pass
            except Exception as e:
                logging.debug("we got bad data from "+str(address))
                logging.debug(traceback.format_exc())
        return data, address

    def sendData(self,sock,address,subject,body,recipient):
        message = {"subject":subject,"body":body,"recipient":recipient}
        #sock.sendto(str(data).encode('utf-8'),address)
        sock.sendto(pickle.dumps(message),address)

    def getTime(self):
        #return the current clock time in milliseconds
        return int(round(time.time() * 1000))

    def keepAlive(self,sock):
        currentTime = self.getTime()

        #if this code runs, we are having network issues, and should consider ourselves disconnected
        if((currentTime-self.lastUpdate) > self.keepaliveDelay+self.connectionTimeout):
            logging.debug("Keepalive failed to send for "+str(self.connectionTimeout/1000.0)+" seconds. Let's consider ourselves disconnected.")
            self.lastUpdate = currentTime
            return False

        if((currentTime-self.lastUpdate) > self.keepaliveDelay):
            try:
                self.sendData(sock,(self.serverAddress,self.port),"keepalive","","")
                self.lastUpdate = currentTime
            except Exception as e:
                #one of a few things may have happened
                #either the OS is blocking our send for some reason (buffer full?),
                #our pi is not connected to wifi
                #or gatemaster is not available on the network
                logging.debug("Failed to send keepalive. We may get disconnected")
                logging.debug(traceback.format_exc())
        return True

    def restartProcess(self,sock):
        #lets close the datagram socket
        logging.debug("closing socket...")
        sock.close()
        #Restarts the current program, with file objects and descriptors cleanup
        try:
            logging.debug("restarting process...")
            p = psutil.Process(os.getpid())
            for handler in p.get_open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            logging.debug(traceback.format_exc())

        python = sys.executable
        os.execl(python, python, *sys.argv)
        if(self.devMode == False):
            LED.customColor([0,255,0])

    def pullBranch(self,sock,branch,LED):
        if(self.devMode == False):
            LED.customColor([255,0,0])
        #let's call the linux commands to pull the repo down
        #we assume you have an ssh key setup
        logging.debug("pulling latest repo changes")
        currentDirectory = sys.path[0]
        if(self.devMode == False):
            os.system("cd "+currentDirectory+" && git fetch && git reset --hard && git checkout "+str(branch)+" && git pull origin "+str(branch)+" && exit")
        else:
            print("cd "+currentDirectory+" && git fetch && git reset --hard && git checkout "+str(branch)+" && git pull origin "+str(branch)+" && exit")
        #we need to restart this python script to see the changes
        if(self.devMode == False):
            LED.customColor([0,255,0])
        self.restartProcess(sock)

    def shutdown(self,sock,LED):
        if(self.devMode == False):
            LED.customColor([255,0,0])
            time.sleep(0.5)
            LED.customColor([0,255,0])
            time.sleep(0.5)
            LED.customColor([255,0,0])
            time.sleep(0.5)
            LED.customColor([0,255,0])
            time.sleep(0.5)
        #let's call the linux commands to shutdown the pis
        logging.debug("shutting down Pis...")
        if(self.devMode == False):
            sock.close()
            os.system("sudo shutdown -h now")
        else:
            print("sudo shutdown -h now")

    def reboot(self,sock,LED):
        if(self.devMode == False):
            LED.customColor([255,0,0])
            time.sleep(0.5)
            LED.customColor([0,255,0])
            time.sleep(0.5)
        #let's call the linux commands to shutdown the pis
        logging.debug("rebooting Pis...")
        if(self.devMode == False):
            sock.close()
            os.system("sudo shutdown -r now")
        else:
            print("sudo shutdown -r now")

    def runProgram(self,sock,LED):
        gate = DSUtils.Gate(sock,(self.serverAddress,self.port),self.defaultColor)
        if self.connectToServer(sock,(self.serverAddress,self.port),LED):
            while(True):
                self.readSerial()
                newUpdate = False
                if self.keepAlive(sock): #let's let the server know we're still there
                    data,address = self.recvData(sock)
                    self.updateAnimations(LED)
                    if(data):
                        if(self.handleMessage(sock,address,data,LED)): #if this returns false, we've been disconnected
                            pass
                        else:
                            break
                else:
                    break #something went wrong. let's start over

        logging.debug("disconnected")

    def updateAnimations(self,LED):
        if(self.devMode==False):
            try:
                if self.tempAnimationQueue == []: #if we don't have any temporary animations to get through
                    #lets figure out what animation/color we should be playing
                    if(self.currentColor=="breathing"):
                        #LED.breathing()
                        colors = []
                        totalGain = 0
                        for i in range(0,len(self.pilots)):
                            pilot = self.pilots[i]
                            color = [0,0,0]
                            gain = 1-(pilot.distance-1.5)
                            if(gain >= 1):
                                gain = 1
                            if(gain <= 0):
                                gain = 0
                            totalGain += gain
                            color = [pilot.color[0]*gain,pilot.color[1]*gain,pilot.color[2]*gain]
                            colors.append(color)

                        if totalGain > 1:
                            totalGain = 1

                        #lets add all the colors together and normalize them
                        color = [0,0,0]
                        for i in range(0,len(colors)):
                            for j in range(0,len(color)):
                                color[j]=color[j]+colors[i][j]

                        lum = color[0]+color[1]+color[2]
                        if(lum<=0.01):
                            lum = 0.01
                        for i in range(0,len(color)):
                            color[i]=(color[i]/lum)*255*totalGain
                        LED.customColor(color)

                    elif(self.currentColor=="chasing"):
                        LED.chasing()
                    elif(self.currentColor=="rainbow"):
                        LED.rainbow()
                    elif(self.currentColor=="pacman"):
                        LED.pacman()
                    else: #it must be a list of rgb values
                        try:
                            LED.customColor(self.currentColor)
                        except:
                            logging.debug("Color or animation \""+str(self.currentColor)+"\" not recognized")
                            logging.debug("playing default instead")
                            self.currentColor = self.defaultColor
                            LED.rainbow()
                else:#lets play our temp animation
                    animationInProgress = False
                    if self.tempAnimationQueue[0] == "flashbang":
                        animationInProgress = LED.tempFlash() #let's flash until this function returns false
                    if self.tempAnimationQueue[0] == "bluebang":
                        animationInProgress = LED.tempFlashBlue()
                    if self.tempAnimationQueue[0] == "greenbang":
                        animationInProgress = LED.tempFlashGreen()
                    if self.tempAnimationQueue[0] == "redbang":
                        animationInProgress = LED.tempFlashRed()
                    if animationInProgress == False:
                        del self.tempAnimationQueue[0] #animation is finished, remove it from the queue
            except Exception as e:
                logging.debug(traceback.format_exc())

    def handleMessage(self,sock,address,data,LED):
        if(data):
            try:
                subject = data['subject'] #the subject of the message ()
                body = data['body'] #the body of the message
                recipient = data['recipient'] #the intended recipient. If there isn't one, the message is for everyone
                logging.debug("recieved data: "+str(data))
                if(subject == "disconnect"):
                    logging.debug("we recieved a disconnect request")
                    return False; #we gotta bail out

                if(subject == "getLapList"):
                    responseAddress = body['responseAddress']
                    body['response'] = self.getSendableLaps()
                    logging.debug("we recieved a lap list request")
                    self.sendData(sock,(self.serverAddress,self.port),"return",body,"")
                if(subject == "clearLapList"):
                    self.clearLaps()
                    responseAddress = body['responseAddress']
                    body['response'] = self.getSendableLaps()
                    logging.debug("we recieved a clear lap list request")
                    self.sendData(sock,(self.serverAddress,self.port),"return",body,"")

                if(subject == "updateColor"):
                    self.currentColor = body
                    logging.debug("updating color: "+str(self.currentColor))

                if(subject == "updateAnimation"):
                    self.currentColor = body
                    logging.debug("updating animation: "+str(self.currentColor))
                if(subject == "tempAnimation"):
                    self.tempAnimationQueue.append(body)
                    logging.debug("adding temp animation to queue: "+str(body))
                if(subject == "thetaCommand"):
                    self.writeSerial(body)
                    logging.debug("sending theta command "+body)
                if(subject == "systemCommand"):
                    command = body['command']
                    arguments = body['arguments']
                    logging.debug("performing command: "+command)
                    if(command=="shutdown"):
                        self.shutdown(sock,LED)
                    if(command=="reboot"):
                        self.reboot(sock,LED)
                    if(command=="update"):
                        branch = arguments[0]
                        self.pullBranch(sock,branch,LED)

            except Exception as e:
                logging.debug(traceback.format_exc())
                return False
        else:
            return False
        return True #everything went well

    def start(self):
        logging.debug("using server address "+str(self.serverAddress))
        logging.debug("using port "+str(self.port))
        logging.debug("starting with "+str(self.ledCount)+" LEDs")

        self.arduinoConnected = self.connectArduino()

        if(self.devMode==False):
            LED = LEDUtils.LEDStrip(self.ledCount)
        else:
            LED = 0
        sock = self.createSocket(13246)
        while(True):
            try:
                self.runProgram(sock, LED)
            except Exception as e:
                time.sleep(3) #lets sleep so we don't end up spamming connection requests
                logging.debug(traceback.format_exc())
                #for i in range(0,20):
                #    LED.allGrey()
                #LED.clearPixels()
                try:
                    LED.rainbow()
                except Exception as e:
                    logging.debug("Unable to play initial color ")
                    logging.debug(traceback.format_exc())
                logging.debug("no connection to server. Retrying...")
        self.disconnectArduino()
