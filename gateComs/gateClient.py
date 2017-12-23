devMode = False

import socket
import time
import select
import time
import DSUtils
import os
import sys
import logging
import psutil
if(not devMode):
    import LEDUtils

#lets get gateServer address and port from command line, or use defaults
serverAddress = "gatemaster"
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

def restartProcess(sock):
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

def pullMaster(sock):
    #let's call the linux commands to pull the repo down
    #we assume you have an ssh key setup
    branch = "master"
    print("pulling latest repo changes")
    os.system("git reset --hard origin/"+str(branch)+" && git pull origin "+str(branch)+" && exit")
    #we need to restart this python script to see the changes
    restartProcess(sock)

def pullDevelop(sock):
    #let's call the linux commands to pull the repo down
    #we assume you have an ssh key setup
    branch = "develop"
    print("pulling latest repo changes")
    os.system("git reset --hard origin/"+str(branch)+" && git pull origin "+str(branch)+" && exit")
    #we need to restart this python script to see the changes
    restartProcess(sock)

def runProgram(sock,LED):
    gate = DSUtils.Gate(sock,(serverAddress,port),"white")
    connectToServer(sock,(serverAddress,port))
    lastColor = ""
    animation = False
    animationFrame = 0
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
                pullDevelop(sock)
            if(currentColor=="chasing"):
                LED.chasing()
            if(currentColor=="rainbow"):
                LED.rainbow()
            if(currentColor=="pacman"):
                LED.pacman()
        else:
            if(currentColor=="update"):
                pullDevelop(sock)
        gate.keepAlive() #let's let the server know we're still there
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
