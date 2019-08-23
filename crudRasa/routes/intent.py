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

            tmpAct=models.Action(
                action_name='utter_'+data['intent_name'],
                agent_id=data['agent_id']
            )
            
            db.session.add(tmpInt)
            db.session.add(tmpAct)
            db.session.commit()
            
            return utils.result('intent and action added', {
                'intent_id': tmpInt.intent_id,
                'action_id': tmpAct.action_id,
            })
        else:
            return utils.result('intent exists', {'id': tmp.intent_id})
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
            intent_name=intent.intent_name
            intent.update(data)
            action=db.session.query(models.Action)\
                .filter_by(action_name='utter_'+intent_name).first_or_404()
            action.update({'action_name': 'utter_'+data['intent_name']})
            db.session.commit()
            return utils.result('intent and action updated', {
                'intent_id': intent_id,
                'action_id': action.action_id
            })
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method=='DELETE':
        try:
            result=db.session.query(models.Intent)\
                .filter_by(intent_id=intent_id).delete()
            db.session.commit()
            return jsonify({'rowCount':str(result)})
            # return utils.result('success', f'Removed intent {intent_id}')
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
    try:
        intents=db.session.query(models.t_unique_intent_entities)\
            .filter_by(intent_id=intent_id).all()
        return jsonify([models.Helper\
            .serializeStatic(i) for i in intents])
    except Exception as e:
        return(str(e))
