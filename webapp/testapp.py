import os
import random
import time
import uuid
from flask import (
    Flask,
    request,
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
    current_app
)
from celery import Celery
from flask.ext.socketio import (
    SocketIO,
    emit,
    disconnect
)
from requests import post

app = Flask(__name__)
app.debug = True
app.clients = {}
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# SocketIO
socketio = SocketIO(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task(bind=True)
def long_task(self, elementid, userid, url):

    return "hello world"


@app.route('/clients', methods=['GET'])
def clients():
    return jsonify({'clients': app.clients.keys()})


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    return redirect(url_for('index'))


@app.route("/socket", methods=['GET'])
def longtask():
    #from IPython.core.debugger import Tracer; Tracer()()
    task = long_task.delay()
    return "made it!"


@app.route('/event/', methods=['POST'])
def event():
    userid = request.json['userid']
    data = request.json
    ns = app.clients.get(userid)
    if ns and data:
        ns.emit('celerystatus', data)
        return 'ok'
    return 'error', 404


@socketio.on('status', namespace='/events')
def events_message(message):
    emit('status', {'status': message['status']})


@socketio.on('disconnect request', namespace='/events')
def disconnect_request():
    emit('status', {'status': 'Disconnected!'})
    disconnect()


@socketio.on('connect', namespace='/events')
def events_connect():
    userid = str(uuid.uuid4())
    session['userid'] = userid
    current_app.clients[userid] = request.namespace
    emit('userid', {'userid': userid})
    emit('status', {'status': 'Connected user', 'userid': userid})


@socketio.on('disconnect', namespace='/events')
def events_disconnect():
    del current_app.clients[session['userid']]
    print('Client %s disconnected' % session['userid'])


if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app)
