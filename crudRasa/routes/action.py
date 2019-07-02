from flask import request, jsonify, Blueprint

import utils
from app import db
from db import models


action=Blueprint('action', __name__)

@action.route("/actions/<action_id>", methods=['GET', 'PUT', 'DELETE'])
def actionID(action_id):
    if request.method=='PUT':
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
    
    if request.method=='DELETE':
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

@action.route("/actions", methods=['POST'])
def actions():
    try:
        data=request.get_json()
        db.session.add(models.Action(
            action_name=data['action_name'],
            agent_id=data['agent_id']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))

@action.route('/agents/<agent_id>/actions', methods=['GET'])
def agentActions(agent_id):
    try:
        actions=models.Action.query.filter_by(agent_id=agent_id).all()
        return  jsonify([a.serialize() for a in actions])
    except Exception as e:
        return(str(e))
