from flask import request, jsonify, Blueprint

import utils
from app import db
from db import models

intent=Blueprint('intent', __name__)

@intent.route("/intents", methods=['POST'])
def intents():
    try:
        data=request.get_json()
        db.session.add(models.Intent(
            intent_name = data['intent_name'],
            agent_id = data['agent_id']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))

@intent.route("/intents/<intent_id>", methods=['GET', 'PUT', 'DELETE'])
def intentID(intent_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            intent=db.session.query(models.Intent)\
                .filter_by(intent_id=intent_id).first_or_404()
            intent.update(data)
            db.session.commit()
            return utils.result('success', 'Updated intent')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method=='DELETE':
        try:
            db.session.query(models.Intent)\
                .filter_by(intent_id=intent_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed intent {intent_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))

    try:
        intent=models.Intent.query\
            .filter_by(intent_id=intent_id).first_or_404()
        return jsonify(intent.serialize())
    except Exception as e:
	    return(str(e))


@intent.route('/agents/<agent_id>/intents', methods=['GET', 'POST'])
def agentIntents(agent_id):
    if request.method=='POST':
        try:
            data=request.get_json()
            db.session.add(models.Intent(
                intent_name = data['intent_name'],
                agent_id = data['agent_id']
            ))
            db.session.commit()
            return utils.result('success', 'Inserted')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    try:
        intents=models.Intent.query.filter_by(agent_id=agent_id).all()
        return  jsonify([i.serialize() for i in intents])
    except Exception as e:
        return(str(e))


@intent.route('/intents/<intent_id>/unique_intent_entities', methods=['GET'])
def intentUnique(intent_id):
    pass
