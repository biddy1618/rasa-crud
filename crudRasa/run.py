from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import app, db

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

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(port=5010)