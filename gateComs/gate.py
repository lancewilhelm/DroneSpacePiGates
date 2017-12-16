import socket
import sys
import time
import select
import time
import DSUtils

currentColor = "none"
serverAddress = "192.168.1.110"
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
    print("recv: "+str(data.decode('utf-8')))
    return data,address

def sendData(sock,address,data):
    sock.sendto(str(data).encode('utf-8'),address)


def runProgram(sock):
    gate = DSUtils.Gate(sock,(serverAddress,port),"white")
    connectToServer(sock,(serverAddress,port))
    while(True):
        currentColor = recvData(sock)[0]
        gate.keepAlive()

def main():
    sock = createSocket(13246)
    while(True):
        try:
            runProgram(sock)
        except Exception as e:
            print(e)
            time.sleep(3)
            print("no connection to server. Retrying...")

main()
