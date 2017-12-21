import socket
try:
    import cPickle as pickle
except:
    import pickle
def createSocket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    #sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    hostname = socket.gethostbyname('localhost')
    sock.setblocking(0)
    print("binding to "+str(hostname)+" on port "+str(port))
    #sock.bind((hostname,port))
    print("bound")
    return sock
def sendGateUpdate(controllerAddress,controllerPort, animation):
    sock = createSocket(controllerPort)
    message = pickle.dumps({"animation":animation})
    print(message)
    sock.sendto(message,(controllerAddress,controllerPort))
