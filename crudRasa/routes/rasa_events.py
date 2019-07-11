from flask import request, jsonify, Blueprint

from app import db, func
from orm import models, utils


rasa_events=Blueprint('rasa_events', __name__)

'''
INSERT INTO nlu_parse_log(messages_id, intent_name, entity_data, intent_confidence_pct, user_response_time_ms, nlu_response_time_ms) 
VALUES ($(messages_id), $(intent_name), $(entity_data), $(intent_confidence_pct),$(user_response_time_ms),$(nlu_response_time_ms))
'''
@rasa_events.route('/rasa_events/operation1', methods=['POST'])
def operation1():
    try:
        data=request.get_json()
        db.session.add(models.NluParseLog(
            messages_id=data['messages_id'],
            intent_name=data['intent_name'],
            entity_data=data['entity_data'],
            intent_confidence_pct=data['intent_confidence_pct'],
            user_response_time_ms=data['user_response_time_ms'],
            nlu_response_time_ms=data['nlu_response_time_ms']
        ))
        db.session.commit()
        # Empty response - 204 No Content
        return ('', 204)
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
INSERT INTO messages_entities(message_id, entity_id, entity_start, entity_end, entity_value, entity_confidence) 
VALUES ($(message_id), $(entity_id), $(entity_start), $(entity_end), $(entity_value), $(entity_confidence))
'''
@rasa_events.route('/rasa_events/operation2', methods=['POST'])
def operation2():
    try:
        data=request.get_json()
        db.session.add(models.MessagesEntity(
            message_id=data['message_id'],
            entity_id=data['entity_id'],
            entity_start=data['entity_start'],
            entity_end=data['entity_end'],
            entity_value=data['entity_value'],
            entity_confidence=data['entity_confidence']
        ))
        db.session.commit()
        # Empty response - 204 No Content
        return ('', 204)
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
SELECT entity_id, parameter_start, parameter_end, parameter_value 
FROM parameters WHERE expression_id=$(expression_id)
'''
@rasa_events.route('/rasa_events/operation3', methods=['GET'])
def operation3():
    try:
        expression_id=request.args.get('expression_id')
        
        data=models.Parameter.query\
            .filter_by(expression_id=expression_id)\
            .with_entities(
                models.Parameter.entity_id,
                models.Parameter.parameter_start,
                models.Parameter.parameter_end,
                models.Parameter.parameter_value,
            ).all()
        
        return jsonify([{
            'entity_id': e[0],
            'parameter_start': e[1],
            'endpoint_enabled': e[2],
            'parameter_end': e[3],
            'parameter_value': e[4],
            } for e in data])
    except Exception as e:
        return(str(e))


'''
SELECT entity_id FROM entities WHERE entity_name=$(entity)
'''
@rasa_events.route('/rasa_events/operation4', methods=['GET'])
def operation4():
    try:
        entity_name=request.args.get('entity')
        
        data=models.Entity.query.filter_by(entity_name=entity_name)\
            .with_entities(models.Entity.entity_id).all()
        
        return jsonify([{'entity_id': e[0]} for e in data])
    except Exception as e:
        return(str(e))


'''
SELECT expression_id FROM expressions 
WHERE LOWER(expression_text)=LOWER($(message_text))
'''
@rasa_events.route('/rasa_events/operation5', methods=['GET'])
def operation5():
    try:
        message_text=request.args.get('message_text')
        
        data=models.Expression.query.filter(
            func.lower(models.Expression.expression_text)\
                ==func.lower(message_text))\
            .with_entities(models.Expression.expression_id).all()
        
        return jsonify([{'expression_id': e[0]} for e in data])
    except Exception as e:
        return(str(e))


'''
INSERT INTO messages(timestamp, agent_id, user_id, user_name, message_text, message_rich, user_message_ind, intent_id)
VALUES($(timestamp), $(agent_id), $(user_id),$(user_name), $(message_text), $(message_rich), $(user_message_ind), 
(SELECT intent_id FROM intents WHERE intent_name=$(intent_name) and agent_id=$(agent_id)))
RETURNING messages_id'
'''
@rasa_events.route('/rasa_events/operation6', methods=['POST'])
def operation6():
    try:
        data=request.get_json()

        intent_id=models.Intent.query.filter(db.and_(
            models.Intent.intent_name==data['intent_name'],
            models.Intent.agent_id==data['agent_id']
            )).with_entities(models.Intent.intent_id).one()[0]
        
        message=models.Message(
            timestamp=data['timestamp'],
            agent_id=data['agent_id'],
            user_id=data['user_id'],
            user_name=data['user_name'],
            message_text=data['message_text'],
            message_rich=data['message_rich'],
            user_message_ind=data['user_message_ind'],
            intent_id=intent_id,
        )

        db.session.add(message)
        db.session.commit()
        # Empty response - 204 No Content

        return jsonify(message.serialize())
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
SELECT agent_id FROM agents WHERE agent_name=$(agent_name)
'''
@rasa_events.route('/rasa_events/operation7', methods=['GET'])
def operation7():
    try:
        agent_name=request.args.get('agent_name')

        agent_id=models.Agent.query.filter_by(agent_name=agent_name)\
            .with_entities(models.Agent.agent_id).one()[0]
        
        return jsonify([{'agent_id': agent_id}])
    except Exception as e:
        return(str(e))


'''
SELECT agent_id FROM messages WHERE user_id=$(user_id) 
and user_name='user' ORDER BY timestamp DESC LIMIT 1
'''
@rasa_events.route('/rasa_events/operation8', methods=['GET'])
def operation8():
    try:
        user_id=request.args.get('user_id')

        agent_id=models.Message.query.filter_by(user_id=user_id)\
            .with_entities(models.Message.agent_id)\
            .order_by(models.Message.timestamp.desc()).first()[0]
        
        return jsonify([{'agent_id': agent_id}])
    except Exception as e:
        return(str(e))