from flask import Flask, request, render_template
from flask_socketio import SocketIO
import socket
import DSWebClient
import time
import json
import threading
from threading import Thread
from flask import appcontext_tearing_down
#from blink import Blink
#import leddimmer as l
#from getButtonStatus import getButtonStatus
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
gateMasterAddr = ""

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
        laps = DSWebClient.getLapList(gateMasterAddr,13246)
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

@app.route("/socket", methods=['GET'])
def socket():
    return render_template('socket.html')

@socketio.on('join')
def onJoin(data):
    room = data['room']
    join_room(room)
    laps = DSWebClient.getLapList(gateMasterAddr,13246)
    send(str(laps), room=room)

def onNewData(lap):
    room = data['room']
    join_room(room)
    send(str(laps), room=room)

@socketio.on('leave')
def onLeave(data):
    room = data['room']
    leave_room(room)
    send("Goodbye!", room=room)

def listenForGateUpdates(app):

    print("Listen thread has started. Here we go baby!!!")
    sock = DSWebClient.createSocket(13248,1) #lets create a socket in blocking mode
    data,address = DSWebClient.recvData(sock)
    while(True):
        if(data!=None):
            try:
                subject = data['subject'] #the subject of the message
                body = data['body'] #the body of the message
                recipient = data['recipient']
                onNewData(body)
            except:
                print("bad message format")

def startGateServerListener(app):
    gslThread = Thread(target=listenForGateUpdates, args=[app])
    gslThread.start()

@app.before_first_request #we use this so that our thread is a sub process of the reloader
def app_init():
    print("APP STARTING")
    startGateServerListener(app)

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=80, debug=True)
    #
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
