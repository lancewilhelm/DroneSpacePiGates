from flask import Flask, request, render_template
import DSClient
import time
#from blink import Blink
#import leddimmer as l
#from getButtonStatus import getButtonStatus
app = Flask(__name__)

@app.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
      color = request.form['color']
      gateID = request.form['gateID']
      update = request.form['update']

      if color == 'reboot':
        DSClient.sendGateUpdate("localhost",13246,"red")
        time.sleep(0.1)
        DSClient.sendGateUpdate("localhost",13246,"green")
        time.sleep(0.1)
        DSClient.sendGateUpdate("localhost",13246,"reboot")
      elif color == 'shutdown':
        DSClient.sendGateUpdate("localhost",13246,"red")
        time.sleep(0.1)
        DSClient.sendGateUpdate("localhost",13246,"green")
        time.sleep(0.1)
        DSClient.sendGateUpdate("localhost",13246,"red")
        time.sleep(0.1)
        DSClient.sendGateUpdate("localhost",13246,"green")
        time.sleep(0.1)
        DSClient.sendGateUpdate("localhost",13246,"shutdown")
      elif color == 'update':
        DSClient.sendGateUpdate("localhost",13246,"red")
        time.sleep(1)
        DSClient.sendGateUpdate("localhost",13246,"update")
        time.sleep(1)
        DSClient.sendGateUpdate("localhost",13246,"green")
      elif color == 'rainbow':
        DSClient.sendGateUpdate("localhost",13246,"rainbow")
        return 'rainbow'
      elif color == 'red':
        #allRed(strip)
        DSClient.sendGateUpdate("localhost",13246,"red")
        return 'red'
      elif color == 'chasing':
        #chasing(strip)
        DSClient.sendGateUpdate("localhost",13246,"chasing")
        return 'chasing'
      elif color == 'pacman':
        #chasing(strip)
        DSClient.sendGateUpdate("localhost",13246,"pacman")
        return 'pacman'
      elif color == 'green':
        #allGreen(strip)
        DSClient.sendGateUpdate("localhost",13246,"green")
        return 'green'
      elif color == 'yellow':
        DSClient.sendGateUpdate("localhost",13246,"chasing")
        #flashYellow(strip)
        return 'yellow'
    else:
        return render_template('index.html')

if __name__ == "__main__":
  # Create NeoPixel object with appropriate configuration.
  #strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  # Intialize the library (must be called once before other functions).
  #strip.begin()

  app.run(host='0.0.0.0', port=80, debug=True)
