import time
class Gate:
    def __init__(self,sock,address,color):
        self.address = address
        self.color = color
        self.lastUpdate = self.getTime()
        self.socket = sock

    def updateColor(self,color):
        self.color = color
        self.sendData(color)

    def sendData(self,data):
        self.socket.sendto(data.encode('utf-8'),self.address)

    def keepAlive(self):
        currentTime = self.getTime()
        if((currentTime-self.lastUpdate) > 10000):
            self.sendData("keepalive")
            self.lastUpdate = currentTime
            # print("sending keepalive")

    def isAlive(self):
        alive = True
        currentTime = self.getTime()
        if((currentTime-self.lastUpdate) > 2000):
            alive = False
        return alive

    def getTime(self):
        #return the current clock time in milliseconds
        return int(round(time.time() * 1000))
