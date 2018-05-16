from flask import Flask, request, render_template
from flask_socketio import SocketIO
import socket
import DSWebClient
import time
import json
from celery import Celery
import traceback

#from api.testPage import api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

#register routes
#app.register_blueprint(api, url_prefix='/api')

# SocketIO
socketio = SocketIO(app,message_queue='redis://localhost:6379/0')

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
def getMyIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    myIp = s.getsockname()[0]
    s.close()
    return myIp

gateMasterAddr = getMyIp()

done = False

@app.route("/api/gates/system", methods=['POST','GET'])
def sendElementCommand():
    if request.method == 'POST':
        command = request.form['command']
        gateID = request.form['gateID']
        branch = request.form['branch']

        if command == 'reboot':
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"reboot","")
            return "rebooting"
        elif command == 'shutdown':
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"shutdown","")
            return "shutting down"
        elif command == 'update':
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"update",[branch])
            return "updating software"

@app.route("/api/server/gates", methods=['POST','GET'])
def getServerGates():
    gates = DSWebClient.getGateList(gateMasterAddr,13246)
    print(gates)
    return str(gates)

@app.route("/api/server/sensors/timing/laps", methods=['POST','GET','DELETE'])
def getServerTiming():
    if request.method == "GET":
        laps = DSWebClient.getLapList(gateMasterAddr,13246,{})
        print(laps)
        return json.dumps(laps)
    if request.method == "DELETE":
        DSWebClient.clearLapList(gateMasterAddr,13246)
        return json.dumps([])

@app.route("/api/server/sensors/timing/command", methods=['POST','GET'])
def sendSensingCommand():
    if request.method == "POST":
        command = request.form['command']
        DSWebClient.executeThetaCommand(gateMasterAddr,13246,command)
        # print(command)
        return "sending command"

@app.route("/api/gates/color", methods=['POST'])
def setGateColors():
    program = request.form['color']
    red = int(request.form['red'])
    green = int(request.form['green'])
    blue = int(request.form['blue'])
    rgbColor = [red,green,blue]
    gateID = request.form['gateID']
    if(gateID == "all"):
        if(program == "custom" or program == "solid"):
            print("custom or solid")
            DSWebClient.sendGateColor(gateMasterAddr,13246,rgbColor)
        else:
            print("animation")
            DSWebClient.sendGateAnimation(gateMasterAddr,13246,program)
    else:
        DSWebClient.sendSystemCommandTo(gateMasterAddr,gateID,13246,program,"")
    return ""

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/timing", methods=['GET'])
def timing():
    return render_template('timing.html')

@app.route("/configure", methods=['GET'])
def configure():
    return render_template('configure.html')

@socketio.on('getLapList', namespace="/timing")
def timingConnected(data):
    print("got request for lap list")
    getLapsTask = getLapList.delay()

    asdf = "laps cleared"

def emitTimingMessage(subject,message,address):
    print(str(subject)+" at gate "+str(address[0])+ " - "+str(message))
    socketio.emit(subject,json.dumps({"message":message,"gate":address}),namespace="/timing")

def handleNewData(data,address):
    print("handling data "+str(data))
    subject = data['subject'] #the subject of the message
    body = data['body'] #the body of the message
    namespace = body['namespace']
    message = body['message']
    if(namespace=="timing"):
        emitTimingMessage(subject,message,address)

@app.route("/socket", methods=['GET'])
def testSocketStuff():
    return render_template('socket.html')

@celery.task
def getLapList():
    print("getting laps!")
    laps = DSWebClient.getLapList(gateMasterAddr,13246,{})
    #laps = [["sky",10.0,1],["sky",10.0,2],["sky",10.0,3],["sky",10.0,4],["ninja",10.0,1],["ninja",10.0,2],["ninja",10.0,3],["ninja",10.0,4]]
    print("we got some laps back!!!")
    print(laps)
    if(laps==None):
        laps = []
    emitTimingMessage("lap list", laps, ("127.0.0.1",23453))

@celery.task
def startGateEventListener():
    print("Listen thread has started. Here we go baby!!!")
    sock = DSWebClient.createSocket(13249,1) #lets create a socket in blocking mode
    while(True):
        try:
            data,address = DSWebClient.recvData(sock)
            if(data!=None):

                handleNewData(data,address)
        except Exception as e:
            print("unable to handle data: "+str(data))
            print(traceback.format_exc())
    return data

@app.before_first_request
def initAndStuff():
    print("APP STARTING")
    task = startGateEventListener.delay()
    print("APP STARTED")

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=80, debug=True)
    #
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
    done = True
