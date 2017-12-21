devMode = False

import socket
import sys
import time
import select
import time
import DSUtils
if(not devMode):
    import LEDUtils

currentColor = "none"
serverAddress = "gatemaster"
port = 13246

def createSocket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    return sock

def connectToServer(sock,address):
    print("connecting to server")
    sendData(sock,address,"connect")
    currentColor = recvData(sock)[0]

def recvData(sock):
    data, address = sock.recvfrom(4096)
    #print("recv: "+str(data.decode('utf-8')))
    return data,address

def sendData(sock,address,data):
    sock.sendto(str(data).encode('utf-8'),address)


def runProgram(sock,LED):
    gate = DSUtils.Gate(sock,(serverAddress,port),"white")
    connectToServer(sock,(serverAddress,port))
    lastColor = ""
    while(True):
        newUpdate = False

        currentColor = recvData(sock)[0]
        if(lastColor != currentColor):
            print(str(lastColor)+str(currentColor))
            newUpdate = True
        if newUpdate == True:
            print("updating color: "+str(currentColor))
            if(currentColor=="yellow"):
                if(not devMode):
                    LED.allYellow()
                else:
                    print("yellow")
            if(currentColor=="green"):
                if(not devMode):
                    LED.allGreen()
                else:
                    print("green")
            if(currentColor=="red"):
                if(not devMode):
                    LED.allRed()
                else:
                    print("red")
        gate.keepAlive()
        lastColor = currentColor

def main():
    if(not devMode):
        LED = LEDUtils.LEDStrip()
    else:
        LED = 0
    sock = createSocket(13246)
    while(True):
        try:
            runProgram(sock, LED)
        except Exception as e:
            print(e)
            time.sleep(3)
            print("no connection to server. Retrying...")

main()
