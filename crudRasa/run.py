from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import app, db

from routes.action import action
# from routes.action import intent
# from routes.action import agent

app.register_blueprint(action)
# app.register_blueprint(intent)
# app.register_blueprint(agent)

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