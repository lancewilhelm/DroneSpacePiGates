from flask import Flask, request, render_template, render_template, Blueprint

api = Blueprint('testPage', __name__)

@api.route("/configure", methods=['GET'])
def configure():
    return render_template('configure.html')
