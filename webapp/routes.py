import socket
import DSWebClient
from flask import Flask, request, render_template, Blueprint

pages = Blueprint('pages', __name__)

@pages.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@pages.route("/timing", methods=['GET'])
def timing():
    return render_template('timing.html')

@pages.route("/configure", methods=['GET'])
def configure():
    return render_template('configure.html')
