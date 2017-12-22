devMode = True

import socket
import time
import select
import time
import DSUtils
import os
import sys
if(not devMode):
    import LEDUtils

#lets get gateServer address and port from command line, or use defaults
serverAddress = ""
port = 13246
currentColor = "none"

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

def pullMaster():
    pid = os.getpid()
    currentScript = str(sys.argv[0])
    os.system("git reset --hard && git pull origin master && kill "+str(pid)+" && sudo python "+str(currentScript))

def pullDevelop():
    pid = os.getpid()
    currentScript = str(sys.argv[0])
    print("git reset --hard")
    print("git pull origin develop")
    print("kill "+str(pid))
    print("sudo python "+str(currentScript))
    os.system("git reset --hard && git pull origin develop && kill "+str(pid)+" && sudo python "+str(currentScript))
    print("git pull")

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
            if(not devMode):
                if(currentColor=="yellow"):
                    LED.allYellow()
                if(currentColor=="green"):
                    LED.allGreen()
                if(currentColor=="red"):
                    LED.allRed()
                if(currentColor=="update"):
                    pullMaster()
            else:
                if(currentColor=="update"):
                    pullDevelop()
                print(currentColor)
        gate.keepAlive()
        lastColor = currentColor

def main():
    print("using server address "+str(serverAddress))
    print("using port "+str(port))
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
