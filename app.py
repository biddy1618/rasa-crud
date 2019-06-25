from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import models

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/getAgents")
def getAllAgents():
    try:
        books=models.Agent.query.all()
        return  jsonify([e.serialize() for e in books])
    except Exception as e:
	    return(str(e))


if __name__ == '__main__':
    app.run(port=5010)