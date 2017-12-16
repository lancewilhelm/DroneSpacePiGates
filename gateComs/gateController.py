import socket
import sys
import time
import select
import time
import DSUtils
try:
    import cPickle as pickle
except:
    import pickle

serverAddress = ""
port = 13246

gates = []
gateStates = {}

currentAnimation = ["[50,50,50]"]
animationSpeed = 10
fps = 60


def createSocket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #hostname = socket.gethostbyname(socket.gethostname())
    sock.setblocking(0)
    print("binding to "+str(serverAddress)+" on port "+str(port))
    sock.bind((serverAddress,port))
    print("bound")
    return sock

def getTime():
    #return the current clock time in milliseconds
    return int(round(time.time() * 1000))

def connectNewGate(sock,address):
    initialGateColor = "white"
    if(address not in gates):
        newGate = DSUtils.Gate(sock,address,initialGateColor)
        gates.append(newGate)
        print("gate "+str(address)+" connected")
    else:
        print("gate "+str(address)+" reconnected")
    newGate.updateColor(initialGateColor)

def recvData(sock):
    global currentAnimation
    data = None
    try:
        data, address = sock.recvfrom(4096)
        try:
            data = data.decode(encoding='utf-8')
        except:
            pass
    except: #there was no message
        pass #let's move on
    if(data):
        if(data == "connect"):
            print("incoming connection...")
            connectNewGate(sock,address)
        else:
            gate = getGateByAddress(address)
            if(data == "keepalive"):
                gate.lastUpdate = getTime()
                print("keep gate "+str(address)+ "alive")
            else:
                print("----------------")
                data = pickle.loads(str(data))
                print(data)
                newAnimation = data['animation']
                for gate in gates:
                    currentAnimation = newAnimation


def getGateByAddress(address):
    for gate in gates:
        if(gate.address == address):
            return gate

def sendData(sock,address,data):
    sock.sendto(str(data).encode(encoding='utf-8'),address)

def recvGateState(sock):
    data = sock.recvfrom(4096).decode(encoding='utf-8')

def runProgram(sock):
    global currentAnimation
    print(currentAnimation)
    while(True):
        for color in currentAnimation:
            frameStart = getTime()
            disconnectedGates = []
            for gate in gates:
                if(gate.isAlive()):
                    gate.updateColor(color)
                else:
                    disconnectedGates.append(gate)
            recvData(sock) #lets listen for data (new gates, lap times etc...)

            #lets disconnect gates that didn't send us a keepAlive in time
            for gate in disconnectedGates:
                print("gate "+str(gate.address)+" disconnected")
                gates.remove(gate)
            frameEnd = getTime()

            #lets sleep until it's time to refresh the gates
            frameDuration = float(frameEnd)-float(frameStart)

            time.sleep(1.0/fps)
            loopEnd = getTime()
            loopDuration = loopEnd-frameStart
            actualFPS = round((1.0/loopDuration)*1000,0)
            print("fps: "+str(actualFPS))


def main():
    global Gate
    sock = createSocket(port)

    runProgram(sock)

main()
