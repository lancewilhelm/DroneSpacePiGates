import time
import logging
try:
    import cPickle as pickle
except:
    import pickle

#any script that wants nice logging can use this function
def startLogging(argLevel,argFile):
    logLevel = logging.WARNING
    if(argLevel=="off"):
        logLevel = logging.ERROR
    elif(argLevel=="low"):
        logLevel = logging.WARNING
    elif(argLevel=="medium"):
        logLevel = logging.DEBUG
    elif(argLevel=="high"):
        logLevel = logging.INFO
    logging.basicConfig(filename=argFile,level=logLevel)

def broadcastColor(sock, port, color):
    broadcastData(sock, port,"updateColor",color,"")

def broadcastData(sock, port,subject,body,recipient):
    message = {"subject":subject,"body":body,"recipient":recipient}
    #sock.sendto(str(data).encode('utf-8'),address)
    sock.sendto(pickle.dumps(message),('255.255.255.0',port))
class Gate: #this is our representation of a gate
    def __init__(self,sock,address,color):
        self.address = address
        self.color = color
        self.lastUpdate = self.getTime()
        self.socket = sock

    def updateAnimation(self,animation):
          self.animation = animation
          self.sendData("updateAnimation",animation,"")

    def updateSolidColor(self,color):
          self.color = color
          self.sendData("updateColor",color,"")

    def sendSystemCommand(self,command,arguments):
          body = {"command":command,"arguments":arguments}
          self.sendData("systemCommand",body,"")

    def sendData(self,subject,body,recipient):
        message = {"subject":subject,"body":body,"recipient":recipient}
        #sock.sendto(str(data).encode('utf-8'),address)
        self.socket.sendto(pickle.dumps(message),self.address)

    def keepAlive(self):
        currentTime = self.getTime()
        if((currentTime-self.lastUpdate) > 2000):
            self.sendData("keepalive","","")
            self.lastUpdate = currentTime
    def setLastKeepalive(self):
        currentTime = self.getTime()
        self.lastUpdate = currentTime

    def isAlive(self):
        alive = True
        currentTime = self.getTime()
        if((currentTime-self.lastUpdate) > 10000):
            alive = False
        return alive

    def getTime(self):
        #return the current clock time in milliseconds
        return int(round(time.time() * 1000))
