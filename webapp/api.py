import socket
import DSWebClient
from flask import Blueprint, request
from flask import current_app as app
import json

api = Blueprint('api', __name__)

@api.route("/gates/system", methods=['POST','GET'])
def sendElementCommand():
    if request.method == 'POST':
        command = request.form['command']
        gateID = request.form['gateID']
        branch = request.form['branch']

        if command == 'reboot':
            DSWebClient.sendSystemCommand(app.config['GATE_SERVER_IP'],app.config['GATE_SERVER_PORT'],"reboot","")
            return "rebooting"
        elif command == 'shutdown':
            DSWebClient.sendSystemCommand(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"],"shutdown","")
            return "shutting down"
        elif command == 'update':
            DSWebClient.sendSystemCommand(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"],"update",[branch])
            return "updating software"

@api.route("/server/gates", methods=['POST','GET'])
def getServerGates():
    gates = DSWebClient.getGateList(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"])
    print(gates)
    return str(gates)

@api.route("/server/sensors/timing/laps", methods=['POST','GET','DELETE'])
def getServerTiming():
    if request.method == "GET":
        laps = DSWebClient.getLapList(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"],{})
        print(laps)
        return json.dumps(laps)
    if request.method == "DELETE":
        DSWebClient.clearLapList(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"])
        return json.dumps([])

@api.route("/server/sensors/timing/command", methods=['POST','GET'])
def sendSensingCommand():
    if request.method == "POST":
        command = request.form['command']
        DSWebClient.executeThetaCommand(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"],command)
        # print(command)
        return "sending command"

@api.route("/gates/color", methods=['POST'])
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
            DSWebClient.sendGateColor(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"],rgbColor)
        else:
            print("animation")
            DSWebClient.sendGateAnimation(app.config['GATE_SERVER_IP'],app.config["GATE_SERVER_PORT"],program)
    else:
        DSWebClient.sendSystemCommandTo(app.config['GATE_SERVER_IP'],gateID,app.config["GATE_SERVER_PORT"],program,"")
    return ""
