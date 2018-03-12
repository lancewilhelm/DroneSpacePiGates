import socket
try:
    import cPickle as pickle
except:
    import pickle
def createSocket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    #sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    hostname = ""
    sock.setblocking(0)
    #print("binding to "+str(hostname)+" on port "+str(port))
    #sock.bind((hostname,port))
    #print("bound")
    return sock

def recvData(sock): #this is where we handle all recieved data
    data = None
    address = None
    try:
        data, address = sock.recvfrom(4096)
    except:
        pass
    if(data):
        data = pickle.loads(data)
        print("----------------")
        print(address)
        print(data)
        subject = data['subject'] #the subject of the message
        body = data['body'] #the body of the message
        recipient = data['recipient'] #the intended recipient of the massage. This may be blank. If so, it's for everyone
        #try:
        #    data = data.decode(encoding='utf-8')
        #except:
        #    pass
    return data, address

def sendDataToServer(sock,address,subject,body,recipient):
    message = {"subject":subject,"body":body,"recipient":recipient}
    #sock.sendto(str(data).encode('utf-8'),address)
    #print(message)
    sock.sendto(pickle.dumps(message),address)

def sendGateAnimation(ip,port,animation):
    sock = createSocket(port)
    sendDataToServer(sock,(ip,port),"updateAnimation",animation,"")

def sendTempAnimation(ip,port,animation):
    sock = createSocket(port)
    sendDataToServer(sock,(ip,port),"tempAnimation",animation,"")

def sendGateColor(ip,port,color):
    sock = createSocket(port)
    sendDataToServer(sock,(ip,port),"updateColor",color,"")

def sendSystemCommand(ip,port,command,arguments):
    sock = createSocket(port)
    body = {"command":command,"arguments":arguments}  #arguments should be a list!
    sendDataToServer(sock,(ip,port),"systemCommand",body,"")

def getGateList(ip,port):
    sock = createSocket(port)
    sendDataToServer(sock,(ip,port),"getGateList","","")
    sock.settimeout(10)
    data,address = recvData(sock)
    result = None
    if(data): #if we got something back
        result = data['body'] #set the result to the body of the message

    return result #this will return None if there was no response

def sendSensorCommand(ip,port,body):
    sock = createSocket(port)
    sendDataToServer(sock,(ip,port),"sensingCommand",body,"")
    sock.settimeout(10)
    data,address = recvData(sock)
    result = None
    if(data): #if we got something back
        result = data['body']['response'] #set the result to the body of the message

    return result #this will return None if there was no response

def getLapList(ip,port):
    return sendSensorCommand(ip,port,"getLapList","")

def clearLapList(ip,port):
    return sendSensorCommand(ip,port,"clearLapList","")
