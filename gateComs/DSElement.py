devMode = False

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

try:
    import LEDUtils
except ImportError:
    pass


try:
    import cPickle as pickle
except:
    import pickle

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
        print("starting DSElement with args "+str(args))
        global devMode
        devMode = args.d
        if(devMode==False): #if we are in dev mod, we won't load pi specific libraries
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
        self.ledCount = args.e
        print("made it to the end")


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
        sock.settimeout(10)
        data,address = self.recvData(sock)
        self.handleMessage(data)
        logging.debug(self.currentColor)
        logging.debug("got connection response "+str(data))
        sock.settimeout(2)
        sock.setblocking(0) #allow the program to return with no data once again

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
                logging.warning(traceback.format_exc())
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
            logging.warning(traceback.format_exc())

        python = sys.executable
        os.execl(python, python, *sys.argv)
        if(devMode == False):
            LED.customColor([0,255,0])

    def pullBranch(self,sock,branch,LED):
        if(devMode == False):
            LED.customColor([255,0,0])
        #let's call the linux commands to pull the repo down
        #we assume you have an ssh key setup
        logging.debug("pulling latest repo changes")
        currentDirectory = sys.path[0]
        if(devMode == False):
            os.system("cd "+currentDirectory+" && git fetch && git reset --hard && git checkout "+str(branch)+" && git pull origin "+str(branch)+" && exit")
        else:
            print("cd "+currentDirectory+" && git fetch && git reset --hard && git checkout "+str(branch)+" && git pull origin "+str(branch)+" && exit")
        #we need to restart this python script to see the changes
        if(devMode == False):
            LED.customColor([0,255,0])
        self.restartProcess(sock)

    def shutdown(self,sock,LED):
        if(devMode == False):
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
        if(devMode == False):
            sock.close()
            os.system("sudo shutdown -h now")
        else:
            print("sudo shutdown -h now")

    def reboot(self,sock,LED):
        if(devMode == False):
            LED.customColor([255,0,0])
            time.sleep(0.5)
            LED.customColor([0,255,0])
            time.sleep(0.5)
        #let's call the linux commands to shutdown the pis
        logging.debug("rebooting Pis...")
        if(devMode == False):
            sock.close()
            os.system("sudo shutdown -r now")
        else:
            print("sudo shutdown -r now")

    def runProgram(self,sock,LED):
        gate = DSUtils.Gate(sock,(self.serverAddress,self.port),"rainbow")
        self.connectToServer(sock,(self.serverAddress,self.port))
        self.currentColor = "none"

        while(True):
            time.sleep(0.02)
            newUpdate = False
            gate.keepAlive() #let's let the server know we're still there
            data,address = self.recvData(sock)

            if(devMode==False):
                try:
                    if(self.currentColor=="breathing"):
                        LED.breathing()
                    if(self.currentColor=="chasing"):
                        LED.chasing()
                    if(self.currentColor=="rainbow"):
                        LED.rainbow()
                    if(self.currentColor=="pacman"):
                        LED.pacman()
                except Exception as e:
                    logging.warning(traceback.format_exc())

            if(data):
                if(self.handleMessage(data)): #if this returns false, we've been disconnected
                    pass
                else:
                    break

        logging.debug("disconnected")

    def handleMessage(self,data):
        subject = data['subject'] #the subject of the message ()
        body = data['body'] #the body of the message
        recipient = data['recipient'] #the intended recipient. If there isn't one, the message is for everyone
        logging.debug("recieved data")
        if(subject == "disconnect"):
            logging.debug("we recieved a disconnect request")
            return False; #we gotta bail out
        if(subject == "updateColor"):
            self.currentColor = body
            logging.debug("updating color: "+str(self.currentColor))
            if(devMode == False):
                LED.customColor(body)
        if(subject == "updateAnimation"):
            self.currentColor = body
            logging.debug("updating animation: "+str(self.currentColor))
        if(subject == "systemCommand"):
            command = body['command']
            arguments = body['arguments']
            logging.debug("performing command: "+command)
            if(command=="shutdown"):
                self.shutdown(sock)
            if(command=="reboot"):
                self.reboot(sock)
            if(command=="update"):
                branch = arguments[0]
                self.pullBranch(sock,branch)

        return True; #everything went well

    def start(self):
        print("calling start")
        logging.debug("using server address "+str(self.serverAddress))
        logging.debug("using port "+str(self.port))
        logging.debug("starting with "+str(self.ledCount)+" LEDs")
        if(devMode==False):
            LED = LEDUtils.LEDStrip(self.ledCount)
            pass
        else:
            LED = 0
        sock = self.createSocket(13246)
        print("starting while loop")
        while(True):
            try:
                self.runProgram(sock, LED)
            except Exception as e:
                logging.warning(traceback.format_exc())
                #for i in range(0,20):
                #    LED.allGrey()
                #LED.clearPixels()
                try:
                    LED.rainbow()
                except Exception as e:
                    logging.debug("Unable to play initial color ")
                    logging.warning(traceback.format_exc())
                logging.debug("no connection to server. Retrying...")
        print("done with while loop somehow")
