from flask import Flask, request, render_template
import DSWebClient
import time
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
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"red","")
            time.sleep(0.1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"green","")
            time.sleep(0.1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"reboot","")
            return "rebooting"
        elif command == 'shutdown':
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"red","")
            time.sleep(0.1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"green","")
            time.sleep(0.1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"red","")
            time.sleep(0.1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"green","")
            time.sleep(0.1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"shutdown","")
            return "shutting down"
        elif command == 'update':
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"red","")
            time.sleep(1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"update",branch)
            time.sleep(1)
            DSWebClient.sendSystemCommand(gateMasterAddr,13246,"green","")
            return "updating software"

@app.route("/api/server/gates", methods=['POST','GET'])
def getServerGates():
    gates = DSWebClient.getGateList(gateMasterAddr,13246)
    print(gates)
    return str(gates)

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

if __name__ == "__main__":
    # Create NeoPixel object with appropriate configuration.
    #strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    #strip.begin()

    app.run(host='0.0.0.0', port=80, debug=True)
