import socket
import sys
import time
import select
import time
import DSUtils
import logging
import traceback
logLevel = None
try:
    logLevel = sys.argv[1]
except:
    pass
if(logLevel):
    if(sys.argv[1] == "d"): #we are running the server on the pi in debug mode
        logging.basicConfig(filename='/home/pi/DSServer.log',level=logging.DEBUG)
    elif(sys.argv[1] == "l"): #we are running the server NOT on a pi
        logging.basicConfig(filename='DSServer.log',level=logging.DEBUG)
else: #we are running the server on a pi
    logging.basicConfig(filename='/home/pi/DSServer.log',level=logging.WARNING)
try:
    import cPickle as pickle
except:
    import pickle

import sys

printFPS = False

serverAddress = ""
port = 13246

gates = []
gateStates = {}

animationSpeed = 10
fps = 10


def createSocket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #hostname = socket.gethostbyname(socket.gethostname())
    sock.setblocking(0)
    logging.debug("binding to "+str(serverAddress)+" on port "+str(port))
    sock.bind((serverAddress,port))
    logging.debug("bound")
    return sock

def getTime():
    #return the current clock time in milliseconds
    return int(round(time.time() * 1000))

def connectNewGate(sock,address,initialGateColor):
    if(address not in gates):
        newGate = DSUtils.Gate(sock,address,initialGateColor)
        gates.append(newGate)
        logging.debug("gate "+str(address)+" connected")
    else:
        logging.debug("gate "+str(address)+" reconnected")
    newGate.updateColor(initialGateColor)

def recvData(sock): #this is where we handle all recieved data
    data = None
    address = None
    try:
        data, address = sock.recvfrom(1024)
        try:
            data = pickle.loads(data)
        except Exception as e:
            logging.warning("got bad data from client at "+str(address))
    except:
        pass
    if(data):
        #logging.debug("----------------")
        #logging.debug(address)
        #logging.debug(data)
        subject = data['subject'] #the subject of the message
        body = data['body'] #the body of the message
        recipient = data['recipient'] #the intended recipient of the massage. This may be blank. If so, it's for everyone
        #try:
        #    data = data.decode(encoding='utf-8')
        #except:
        #    pass
    return data, address


def getGateByAddress(address):
    g = None
    for gate in gates:
        if(gate.address == address):
            g = gate

    if(g):
        pass
    else:
        logging.warning("could not find gate by address "+str(address)+" in list of gates "+str(gates))
    return g

def getGateAddresses():
    result = []
    for gate in gates:
        result.append(str(gate.address))
    return result

def sendDataTo(sock,address,subject,body,recipient):
    message = {"subject":subject,"body":body,"recipient":recipient}
    #sock.sendto(str(data).encode('utf-8'),address)
    sock.sendto(pickle.dumps(message),address)

def sendDisconnect(sock,address):
    sendDataTo(sock,address,"disconnect","","")

def runProgram(sock):
    currentColor = "none"
    while(True):
        disconnectedGates = []
        frameStart = getTime()
        for gate in gates:
            if(gate.isAlive()):
                gate.updateColor(currentColor)
            else:
                disconnectedGates.append(gate)
                sendDisconnect(sock,gate.address)
        data,address = recvData(sock) #lets listen for data (new gates, lap times etc...)
        if(data): #if we got some usable data from the buffer
            subject = data['subject'] #the subject of the message ()
            body = data['body'] #the body of the message
            recipient = data['recipient'] #the intended recipient. If there isn't one, the message is for everyone

            if(subject == "connect"):
                try:
                    connectNewGate(sock,address,currentColor)
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
            if(subject == "updateAllGateColors"):
                try:
                    currentColor = body
                    for gate in gates:
                        gate.updateColor(body)
                    logging.debug("UPDATE ALL GATE COLORS")
                    logging.info(str(gates))
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
            if(subject == "getGateList"):
                sendDataTo(sock,address,"gateList",getGateAddresses(),"")
            if(subject == "keepalive"):
                try:
                    try:
                        getGateByAddress(address).setLastKeepalive()
                    except Exception as e:
                        logging.debug(e)
                        logging.warning(traceback.format_exc())
                        logging.debug("gate with address "+str(address)+ "tried to send a keepalive but isn't in our connection list")
                        logging.debug("sending reconnect request")
                        #sendDisconnect(sock,address)
                        connectNewGate(sock,address,currentColor)
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())


        #lets disconnect gates that didn't send us a keepAlive in time
        for gate in disconnectedGates:
            logging.debug("gate "+str(gate.address)+" disconnected")
            sendDisconnect(sock,gate.address)
            gates.remove(gate)
        frameEnd = getTime()

        #lets sleep until it's time to refresh the gates
        frameDuration = float(frameEnd)-float(frameStart)

        time.sleep(1.0/fps)
        loopEnd = getTime()
        loopDuration = loopEnd-frameStart
        actualFPS = round((1.0/loopDuration)*1000,0)


def main():
    global Gate
    while(True):
        #try:
        sock = createSocket(port)

        runProgram(sock)
        #except Exception as e:
        #    print(e)

main()
sys.stdout.close()
