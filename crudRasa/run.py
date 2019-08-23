from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from app import app, db

from orm import utils

from routes.action import action
from routes.intent import intent
from routes.agent import agent
from routes.expression import expression
from routes.entity import entity
from routes.regex import regex
from routes.synonym import synonym
from routes.variant import variant
from routes.setting import setting
from routes.response import response
from routes.parameter import parameter
from routes.log import log
from routes.nlu_router import nlu_router
from routes.middleware import middleware
from routes.rasa_events import rasa_events
from routes.messages import messages
from routes.auth import auth
from routes.analytics import analytics
from routes.upload import fileUpload

app.register_blueprint(action)
app.register_blueprint(intent)
app.register_blueprint(agent)
app.register_blueprint(expression)
app.register_blueprint(variant)
app.register_blueprint(entity)
app.register_blueprint(regex)
app.register_blueprint(synonym)
app.register_blueprint(setting)
app.register_blueprint(response)
app.register_blueprint(parameter)
app.register_blueprint(log)
app.register_blueprint(nlu_router)
app.register_blueprint(middleware)
app.register_blueprint(rasa_events)
app.register_blueprint(messages)
app.register_blueprint(auth)
app.register_blueprint(analytics)
app.register_blueprint(fileUpload)

@app.before_request
def before_request():
    if request.method != 'OPTIONS' and not utils.checkAuth(request.headers.get('Authorization')):
        return (utils.result(status='Failed', message='authorization failed'), 401)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)