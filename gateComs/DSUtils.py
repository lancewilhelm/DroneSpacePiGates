import time
try:
    import cPickle as pickle
except:
    import pickle
class Gate: #this is our representation of a gate
    def __init__(self,sock,address,color):
        self.address = address
        self.color = color
        self.lastUpdate = self.getTime()
        self.socket = sock

    def updateColor(self,color):
        self.color = color
        self.sendData("updateColor",color,"")

    def sendData(self,subject,body,recipient):
        message = {"subject":subject,"body":body,"recipient":recipient}
        #sock.sendto(str(data).encode('utf-8'),address)
        self.socket.sendto(pickle.dumps(message),self.address)

    def keepAlive(self):
        currentTime = self.getTime()
        if((currentTime-self.lastUpdate) > 3000):
            self.sendData("keepalive","","")
            self.lastUpdate = currentTime
            # print("sending keepalive")
    def setLastKeepalive(self):
        currentTime = self.getTime()
        self.lastUpdate = currentTime

    def isAlive(self):
        alive = True
        currentTime = self.getTime()
        if((currentTime-self.lastUpdate) > 30000):
            alive = False
        return alive

    def getTime(self):
        #return the current clock time in milliseconds
        return int(round(time.time() * 1000))
