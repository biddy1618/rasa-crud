from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import models
import utils

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


@app.route("/agents", methods=['GET', 'POST'])
def agents():
    if request.method == 'POST':
        try:
            data = request.get_json()
            db.session.add(models\
                .Agent(agent_name = data['agent_name']))
            db.session.commit()
            return utils.result('success', 'Inserted')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    try:
        agents=models.Agent.query.all()
        return  jsonify([a.serialize() for a in agents])
    except Exception as e:
        return(str(e))

@app.route("/agents/<agent_id>", methods=['GET', 'PUT', 'DELETE'])
def agentsID(agent_id):
    if request.method == 'PUT':
        try:
            data=request.get_json()
            agent=db.session.query(models.Agent)\
                .filter_by(agent_id=agent_id).first_or_404()
            agent.update(data)
            db.session.commit()
            return utils.result('success', 'Updated agent')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method == 'DELETE':
        try:
            db.session.query(models.Intent)\
                .filter_by(agent_id=agent_id).delete()
            db.session.query(models.Action)\
                .filter_by(agent_id=agent_id).delete()
            db.session.query(models.Entity)\
                .filter_by(agent_id=agent_id).delete()
            db.session.query(models.Agent)\
                .filter_by(agent_id=agent_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed agent {agent_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    try:
        agent=models.Agent.query\
            .filter_by(agent_id=agent_id).first_or_404()
        return jsonify(agent.serialize())
    except Exception as e:
	    return(str(e))


@app.route('/agentStory', methods = ['POST'])
def agentStory():
    try:
        data=request.get_json()
        agent=db.session.query(models.Agent)\
            .filter_by(agent_id=data['agent_id']).first_or_404()
        agent.update(data)
        db.session.commit()
        return utils.result('success', 'Updated Story For Agent')
    except Exception as e:
        db.session.rollback()
        return(str(e))


@app.route("/actions/<action_id>", methods=['GET', 'PUT', 'DELETE'])
def actionID(action_id):
    if request.method == 'PUT':
        try:
            data=request.get_json()
            action=db.session.query(models.Action)\
                .filter_by(action_id=action_id).first_or_404()
            action.update(data)
            db.session.commit()
            return utils.result('success', 'Updated action')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method == 'DELETE':
        try:
            db.session.query(models.Action)\
                .filter_by(action_id=action_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed action {action_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))

    try:
        action=models.Action.query\
            .filter_by(action_id=action_id).first_or_404()
        return jsonify(action.serialize())
    except Exception as e:
	    return(str(e))

@app.route("/actions", methods=['POST'])
def actions():
    try:
        data = request.get_json()
        db.session.add(models.Action(
            action_name = data['action_name'],
            agent_id = data['agent_id']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/agents/<agent_id>/actions', methods=['GET'])
def agentActions(agent_id):
    try:
        actions=models.Action.query.filter_by(agent_id=agent_id).all()
        print(actions)
        return  jsonify([a.serialize() for a in actions])
    except Exception as e:
        return(str(e))


if __name__ == '__main__':
    app.run(port=5010)