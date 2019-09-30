from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

intent=Blueprint('intent', __name__)

@intent.route("/intents", methods=['POST'])
def intents():
    try:
        data=request.get_json()

        tmp=models.Intent.query\
            .filter_by(intent_name=data['intent_name']).first()
        if tmp is None:
            tmpInt=models.Intent(
                intent_name = data['intent_name'],
                agent_id = data['agent_id']
            )

            db.session.add(tmpInt)
            db.session.commit()
            
            return utils.result('intent added', {
                'intent_id': tmpInt.intent_id
            })
        else:
            return (f"intent exists with id: {tmp.intent_id}", 400)
    except Exception as e:
        db.session.rollback()
        return(f"Internal server error: {str(e)}", 500)

@intent.route("/intents/<intent_id>", methods=['GET', 'PUT', 'DELETE'])
def intentID(intent_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            intent=db.session.query(models.Intent)\
                .filter_by(intent_id=intent_id).first_or_404()
            intent.update(data)
            db.session.commit()
            return utils.result('intent updated', {
                'intent_id': intent_id
            })
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)
    
    if request.method=='DELETE':
        try:
            result=db.session.query(models.Intent)\
                .filter_by(intent_id=intent_id).delete()
            db.session.commit()
            return jsonify({'rowCount':str(result)})
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)

    try:
        intent=models.Intent.query\
            .filter_by(intent_id=intent_id).first_or_404()
        
        return jsonify({
            'intent_name': intent.intent_name,
            'agent_id': intent.agent_id,
            'endpoint_enabled': intent.endpoint_enabled,
            'intent_id': intent.intent_id
        })
    except Exception as e:
	    return(f"Internal server error: {str(e)}", 500)


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
            return(f"Internal server error: {str(e)}", 500)
    try:
        intents=models.Intent.query.filter_by(agent_id=agent_id).all()
        return  jsonify([i.serialize() for i in intents])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)


@intent.route('/intents/<intent_id>/unique_intent_entities', methods=['GET'])
def intentUnique(intent_id):
    try:
        intents=db.session.query(models.t_unique_intent_entities)\
            .filter_by(intent_id=intent_id).all()
        return jsonify([models.Helper\
            .serializeStatic(i) for i in intents])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)
