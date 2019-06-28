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

app.register_blueprint(action)
app.register_blueprint(intent)
app.register_blueprint(agent)
app.register_blueprint(entity)
app.register_blueprint(regex)
app.register_blueprint(synonym)
'''
Route arguments:

string  (default) accepts any text without a slash
int	    accepts positive integers
float	accepts positive floating point values
path	like string but also accepts slashes
uuid	accepts UUID strings
'''

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(port=5010)