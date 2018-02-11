import socket
import sys
import time
import select
import time
import DSUtils
import logging
import traceback
import argparse

parser = argparse.ArgumentParser(description="Starts a gate server")
parser.add_argument('--h', type=str, help="-h: help\n-l: \n-d: ")
parser.add_argument('-l', default="off", help="log level (high,medium,low,off)")
parser.add_argument('-f', default="/home/pi/DSServer.log", help="location to save the log file")
parser.add_argument('-ledCount', default=337, help="the number of leds this device controls (integer)")
parser.add_argument('-i', default="", help="the ip address of the gateServer")
parser.add_argument('-p', default=13246, help="gateServer port")
args = parser.parse_args()
DSUtils.startLogging(args.l,args.f) #lets use logging to pump our logs to a file instead of printing all over the place
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

fps = 60


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

def connectNewGate(sock,address,initialGateState):
    if(address not in gates):
        newGate = DSUtils.Gate(sock,address,"none")
        gates.append(newGate)
        logging.debug("gate "+str(address)+" connected")
    else:
        logging.debug("gate "+str(address)+" reconnected")
    newGate.sendMessage(initialGateState)

def recvData(sock): #this is where we handle all recieved data
    data = None
    address = None
    try:
        data, address = sock.recvfrom(10240)
        try:
            data = pickle.loads(data)
        except Exception as e:
            logging.warning("got bad data from client at "+str(address))
    except:
        pass
    # if(data):
    #     #logging.debug("----------------")
    #     #logging.debug(address)
    #     #logging.debug(data)
    #     subject = data['subject'] #the subject of the message
    #     body = data['body'] #the body of the message
    #     recipient = data['recipient'] #the intended recipient of the massage. This may be blank. If so, it's for everyone
    #     extras = data['extras']
    #     #try:
    #     #    data = data.decode(encoding='utf-8')
    #     #except:
    #     #    pass
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
    global printFPS
    currentState= "rainbow"
    lastStateUpdate = {"subject":"","body":"","recipient":""}
    while(True):
        disconnectedGates = []
        frameStart = getTime()
        for gate in gates:
            if(gate.isAlive()):
                pass
            else:
                disconnectedGates.append(gate)

        data,address = recvData(sock) #lets listen for data (new gates, lap times etc...)
        if(data): #if we got some usable data from the buffer
            subject = data['subject'] #the subject of the message ()
            body = data['body'] #the body of the message
            recipient = data['recipient'] #the intended recipient. If there isn't one, the message is for everyone
            if(subject == "connect"):
                try:
                    connectNewGate(sock,address,lastStateUpdate)
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
            if(subject == "updateColor"):
                try:
                    color = body
                    for gate in gates:
                        gate.updateSolidColor(color)
                        lastStateUpdate = {"subject":"updateColor","body":color,"recipient":recipient}
                    logging.debug("UPDATE ALL GATE CUSTOM COLORS")
                    logging.info(str(gates))
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
                currentSubject = subject
                currentBody = body
            if(subject == "tempAnimation"):
                try:
                    animation = body
                    for gate in gates:
                        gate.tempAnimation(animation)
                    logging.debug("sending temp animation")
                    logging.info(str(gates))
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
            if(subject == "updateAnimation"):
                try:
                    animation = body
                    for gate in gates:
                        gate.updateAnimation(animation)
                        lastStateUpdate = {"subject":"updateAnimation","body":animation,"recipient":recipient}
                    logging.debug("UPDATE ALL GATE COLORS")
                    logging.info(str(gates))
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
                currentSubject = subject
                currentBody = body
            if(subject == "systemCommand"):
                try:
                    for gate in gates:
                        gate.sendSystemCommand(body)
                    logging.debug("SENDING SYSTEM COMMAND")
                    logging.info(str(gates))
                except Exception as e:
                    logging.debug(e)
                    logging.warning(traceback.format_exc())
                currentSubject = subject
                currentBody = body
            if(subject == "getGateList"):
                sendDataTo(sock,address,"gateList",getGateAddresses(),"")
            if(subject == "getLapList"):
                for gate in gates:
                    gate.sendData(subject,body,recipient)
            if(subject == "returnLapList"):
                sendDataTo(sock,(serverAddress,port),"returnLapList",getGateAddresses(),"")
            if((subject == "keepalive")):
                try:
                    try:
                        getGateByAddress(address).setLastKeepalive()
                    except Exception as e:
                        logging.debug(e)
                        logging.warning(traceback.format_exc())
                        logging.debug("gate with address "+str(address)+ "tried to send a keepalive but isn't in our connection list")
                        logging.debug("lets just connect him like nothing ever happend")
                        connectNewGate(sock,address,lastStateUpdate)
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
        if(data==None):
            time.sleep(1.0/fps)

        else:
            if(subject != "keepalive"):
                logging.debug("respond quickly")
                #let's not use multicast if the router doesn't support it
                for gate in gates:
                    addr = gate.address
                    gate.sendMessage(lastStateUpdate)
                #DSUtils.broadcastColor(sock, port,lastStateUpdate) #only update colors when we got some data that wasn't a keepalive
            time.sleep(1.0/fps)

        loopEnd = getTime()
        loopDuration = loopEnd-frameStart
        try:
            actualFPS = round((1.0/loopDuration)*1000,0)
        except:
            actualFPS = round((1.0/0.0001)*1000,0)
        if(printFPS):
            logging.debug(actualFPS)
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
