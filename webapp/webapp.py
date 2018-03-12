from flask import Flask, request, render_template
import DSWebClient
import time
import json
#from blink import Blink
#import leddimmer as l
#from getButtonStatus import getButtonStatus
app = Flask(__name__)
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
        DSWebClient.sendSensorCommand(gateMasterAddr,13246,command)
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

if __name__ == "__main__":
    # Create NeoPixel object with appropriate configuration.
    #strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    #strip.begin()

    app.run(host='0.0.0.0', port=80, debug=True)
