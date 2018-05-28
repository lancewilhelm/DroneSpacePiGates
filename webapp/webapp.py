from flask import Flask, request
from flask_socketio import SocketIO
import socket
import DSWebClient
import json
from celery import Celery
import traceback
from api import api
from routes import pages


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

app.config['GATE_SERVER_IP'] = ""
app.config["GATE_SERVER_PORT"] = 13246
app.config["GATE_SERVER_WEB_PORT"] = 13249

#register routes
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(pages)

# SocketIO
socketio = SocketIO(app,message_queue='redis://localhost:6379/0')

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

gateMasterAddr = ""
done = False

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

@celery.task
def getLapList():
    print("getting laps!")
    laps = DSWebClient.getLapList(app.config['GATE_SERVER_IP'],app.config['GATE_SERVER_PORT'],{})
    #laps = [["sky",10.0,1],["sky",10.0,2],["sky",10.0,3],["sky",10.0,4],["ninja",10.0,1],["ninja",10.0,2],["ninja",10.0,3],["ninja",10.0,4]]
    print("we got some laps back!!!")
    print(laps)
    if(laps==None):
        laps = []
    emitTimingMessage("lap list", laps, ("127.0.0.1",23453))

@celery.task
def startGateEventListener():
    print("Listen thread has started. Here we go baby!!!")
    sock = DSWebClient.createSocket(app.config["GATE_SERVER_WEB_PORT"],1) #lets create a socket in blocking mode
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
