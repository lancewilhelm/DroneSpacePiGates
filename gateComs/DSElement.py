devMode = False

import socket
import time
import select
import time
import DSUtils
import os
import sys
import logging
try:
    import cPickle as pickle
except:
    import pickle

if(not devMode):
    #import psutil
    import LEDUtils

class gate:
    def __init__(self,ledCount):
        self.ledCount = ledCount

    def start(self):
        element().start()

class pillar:
    def __init__(self,ledCount):
        self.ledCount = ledCount

    def start(self):
        element().start()

class element:
    def __init__(self):
        #lets get gateServer address and port from command line, or use defaults
        self.serverAddress = "localhost"
        self.port = 13246
        self.currentColor = "none"

    def createSocket(self,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        return sock

    def connectToServer(self,sock,address):
        print("connecting to server")
        self.sendData(sock,address,"connect","","")
        print("sent connection request to server")
        print("waiting for server to respond")
        while(True):
            self.currentColor = self.recvData(sock)[0]
            print(self.currentColor)
            break
        print("got server response")

    def recvData(self,sock): #this is where we handle all recieved data
        global currentColor
        data = None
        address = None
        try:
            data, address = sock.recvfrom(4096)
        except:
            pass
        if(data):
            print(data)
            data = pickle.loads(data)
            print("----------------")
            print(data)
            subject = data['subject'] #the subject of the message
            body = data['body'] #the body of the message
            recipient = data['recipient'] #the intended recipient of the massage. This may be blank. If so, it's for everyone
            #try:
            #    data = data.decode(encoding='utf-8')
            #except:
            #    pass
        return data, address

    def sendData(self,sock,address,subject,body,recipient):
        message = {"subject":subject,"body":body,"recipient":recipient}
        #sock.sendto(str(data).encode('utf-8'),address)
        sock.sendto(pickle.dumps(message),address)

    def restartProcess(self,sock):
        #lets close the datagram socket
        print("closing socket...")
        sock.close()
        #Restarts the current program, with file objects and descriptors cleanup
        try:
            print("restarting process...")
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
        print("pulling latest repo changes")
        os.system("git reset --hard origin/"+str(branch)+" && git pull origin "+str(branch)+" && exit")
        #we need to restart this python script to see the changes
        self.reboot(sock)

    def pullDevelop(self,sock):
        #let's call the linux commands to pull the repo down
        #we assume you have an ssh key setup
        branch = "stability"
        print("pulling latest repo changes")
        os.system("git reset --hard origin/"+str(branch)+" && git pull origin "+str(branch)+" && exit")
        #we need to restart this python script to see the changes
        self.reboot(sock)

    def shutdown(self,sock):
        #let's call the linux commands to shutdown the pis
        print("shutting down Pis...")
        sock.close()
        os.system("sudo shutdown now")

    def reboot(self,sock):
        #let's call the linux commands to shutdown the pis
        print("rebooting Pis...")
        sock.close()
        os.system("sudo reboot now")

    def runProgram(self,sock,LED):
        gate = DSUtils.Gate(sock,(self.serverAddress,self.port),"white")
        self.connectToServer(sock,(self.serverAddress,self.port))
        lastColor = ""
        animation = False
        animationFrame = 0
        while(True):
            newUpdate = False
            data,address = self.recvData(sock)
            if(data):
                self.currentColor = data
                if(lastColor != self.currentColor):
                    print(str(lastColor)+str(self.currentColor))
                    newUpdate = True
                if newUpdate == True:
                    print("updating color: "+str(self.currentColor))
                if(not devMode):
                    if(self.currentColor=="yellow"):
                        LED.allYellow()
                    if(self.currentColor=="green"):
                        LED.allGreen()
                    if(self.currentColor=="red"):
                        LED.allRed()
                    if(self.currentColor=="update"):
                        self.pullDevelop(sock)
                    if(self.currentColor=="chasing"):
                        LED.chasing()
                    if(self.currentColor=="rainbow"):
                        LED.rainbow()
                    if(self.currentColor=="pacman"):
                        LED.pacman()
                    if(self.currentColor=="shutdown"):
                        LED.shutdown()
                    if(self.currentColor=="reboot"):
                        LED.reboot()
                else:
                    if(self.currentColor=="update"):
                        self.pullDevelop(sock)
                lastColor = self.currentColor
            gate.keepAlive() #let's let the server know we're still there


    def start(self):
        print("using server address "+str(self.serverAddress))
        print("using port "+str(self.port))
        if(not devMode):
            LED = LEDUtils.LEDStrip(520)
        else:
            LED = 0
        sock = self.createSocket(13246)
        while(True):
            try:
                self.runProgram(sock, LED)
            except Exception as e:
                print(e)
                time.sleep(3)
                print("no connection to server. Retrying...")
