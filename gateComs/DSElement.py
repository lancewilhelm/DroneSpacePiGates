devMode = False

import socket
import time
import select
import time
import DSUtils
import os
import sys
import logging
logging.basicConfig(filename='/home/pi/DSElement.log',level=logging.DEBUG)
try:
    import cPickle as pickle
except:
    import pickle

if(not devMode):
    import psutil
    import LEDUtils

class gate:
    def __init__(self,ledCount):
        self.ledCount = ledCount

    def start(self):
        element(self.ledCount).start()

class pillar:
    def __init__(self,ledCount):
        self.ledCount = ledCount

    def start(self):
        element(self.ledCount).start()

class element:
    def __init__(self,ledCount):
        #lets get gateServer address and port from command line, or use defaults
        self.serverAddress = "gatemaster"
        self.port = 13246
        self.currentColor = "none"
        self.ledCount = ledCount

    def createSocket(self,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        return sock

    def connectToServer(self,sock,address):
        logging.debug("connecting to server")
        self.sendData(sock,address,"connect","","")
        logging.debug("sent connection request to server")
        logging.debug("waiting for server to respond")
        sock.setblocking(1) #freeze the program for up to 5 seconds until we get some data back
        sock.settimeout(2)
        data,address = self.recvData(sock)
        self.currentColor = data['body']
        logging.debug(self.currentColor)
        logging.debug("got server response")
        sock.setblocking(0) #allow the program to return with no data once again

    def recvData(self,sock): #this is where we handle all recieved data
        global currentColor
        data = None
        address = None
        try:
            data, address = sock.recvfrom(4096)
        except:
            pass
        if(data):
            try:
                data = pickle.loads(data)
                logging.debug("----------------")
                subject = data['subject'] #the subject of the message
                body = data['body'] #the body of the message
                recipient = data['recipient'] #the intended recipient of the massage. This may be blank. If so, it's for everyone
                #try:
                #    data = data.decode(encoding='utf-8')
                #except:
                #    pass
            except Exception as e:
                logging.debug("we got bad data from "+str(address))
                logging.debug(e)
        return data, address

    def sendData(self,sock,address,subject,body,recipient):
        message = {"subject":subject,"body":body,"recipient":recipient}
        #sock.sendto(str(data).encode('utf-8'),address)
        sock.sendto(pickle.dumps(message),address)

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
            logging.error(e)

        python = sys.executable
        os.execl(python, python, *sys.argv)

    def pullMaster(self,sock):
        #let's call the linux commands to pull the repo down
        #we assume you have an ssh key setup
        branch = "master"
        logging.debug("pulling latest repo changes")
        os.system("git fetch && git reset --hard origin/"+str(branch)+" && git pull origin "+str(branch)+" && exit")
        #we need to restart this python script to see the changes
        self.restartProcess(sock)

    def pullDevelop(self,sock):
        #let's call the linux commands to pull the repo down
        #we assume you have an ssh key setup
        branch = "develop"
        logging.debug("pulling latest repo changes")
        os.system("sudo git fetch && sudo git pull origin "+str(branch)+" && exit")
        #we need to restart this python script to see the changes
        self.restartProcess(sock)

    def shutdown(self,sock):
        #let's call the linux commands to shutdown the pis
        logging.debug("shutting down Pis...")
        sock.close()
        os.system("sudo shutdown now")

    def reboot(self,sock):
        #let's call the linux commands to shutdown the pis
        logging.debug("rebooting Pis...")
        sock.close()
        os.system("sudo reboot now")

    def runProgram(self,sock,LED):
        gate = DSUtils.Gate(sock,(self.serverAddress,self.port),"grey")
        self.connectToServer(sock,(self.serverAddress,self.port))
        lastColor = ""
        while(True):
            gate.keepAlive() #let's let the server know we're still there
            data,address = self.recvData(sock)
            if(data):
                subject = data['subject'] #the subject of the message ()
                body = data['body'] #the body of the message
                recipient = data['recipient'] #the intended recipient. If there isn't one, the message is for everyone
                if(subject == "disconnect"):
                    logging.debug("we recieved a disconnect request")
                    break;
                if(subject == "updateColor"):
                    self.currentColor = body
                    if(lastColor != self.currentColor):
                        logging.debug(str(lastColor)+str(self.currentColor))
                        newUpdate = True
                    if newUpdate == True:
                        logging.debug("updating color: "+str(self.currentColor))
                    if(not devMode):
                        if(self.currentColor=="shutdown"):
                            self.shutdown()
                        if(self.currentColor=="reboot"):
                            self.reboot()
                    else:
                        if(self.currentColor=="update"):
                            self.pullDevelop(sock)
                    lastColor = self.currentColor
            if(not devMode):
                if(self.currentColor=="yellow"):
                    LED.allYellow()
                if(self.currentColor=="green"):
                    LED.allGreen()
                if(self.currentColor=="red"):
                    LED.allRed()
                if(self.currentColor=="white"):
                    LED.allGrey()
                if(self.currentColor=="blue"):
                    LED.allBlue()
                if(self.currentColor=="flashWhite"):
                    LED.flashGrey()
                if(self.currentColor=="update"):
                    self.pullDevelop(sock)
                if(self.currentColor=="chasing"):
                    LED.chasing()
                if(self.currentColor=="rainbow"):
                    LED.rainbow()
                if(self.currentColor=="pacman"):
                    LED.pacman()
        logging.debug("disconnected")


    def start(self):
        logging.debug("using server address "+str(self.serverAddress))
        logging.debug("using port "+str(self.port))
        logging.debug("starting with "+str(self.ledCount)+" LEDs")
        if(not devMode):
            LED = LEDUtils.LEDStrip(self.ledCount)
        else:
            LED = 0
        sock = self.createSocket(13246)
        while(True):
            try:
                self.runProgram(sock, LED)
            except Exception as e:
                logging.debug(e)
                for i in range(0,20):
                    LED.allGrey()
                LED.clearPixels()
                logging.debug("no connection to server. Retrying...")
