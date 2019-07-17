from flask import request, jsonify, Blueprint

from app import db, func
from orm import models, utils


nlu_router=Blueprint('nlu_router', __name__)

'''
INSERT INTO messages(agent_id, user_id, user_name, message_text, user_message_ind, intent_id)
values($(agent_id), $(user_id),$(user_name), $(request_text), true, (SELECT intent_id FROM intents 
WHERE intent_name=$(intent_name) and agent_id=$(agent_id))) RETURNING messages_id'
'''
@nlu_router.route("/nlu_router/operation1", methods=['POST'])
def operation1():
    try:
        data=request.get_json()
        
        intent_id=models.Intent.query.filter_by(
                intent_name=data['intent_name'], 
                agent_id=data['agent_id']
            ).with_entities(models.Intent.intent_id)\
                .first_or_404()[0]

        message=models.Message(
            agent_id=data['agent_id'],
            user_id=data['user_id'],
            user_name=data['user_name'],
            message_text=data['request_text'],
            user_message_ind=True,
            intent_id=intent_id
        )

        db.session.add(message)
        db.session.commit()

        return jsonify([{"messages_id": str(message.messages_id)}])
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
INSERT INTO nlu_parse_log(intent_name, entity_data, messages_id,intent_confidence_pct, user_response_time_ms,nlu_response_time_ms)
values($(intent_name), $(entity_data), $(messages_id), $(intent_confidence_pct),$(user_response_time_ms),$(nlu_response_time_ms))'
'''
@nlu_router.route("/nlu_router/operation2", methods=['POST'])
def operation2():
    try:
        data=request.get_json()
        
        db.session.add(models.NluParseLog(
            intent_name=data['intent_name'],
            entity_data=data['entity_data'],
            messages_id=data['messages_id'],
            intent_confidence_pct=data['intent_confidence_pct'],
            user_response_time_ms=data['user_response_time_ms'],
            nlu_response_time_ms=data['nlu_response_time_ms'],
        ))
        db.session.commit()

        return
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
INSERT INTO messages(agent_id, user_id, user_name, message_text, message_rich, user_message_ind)
values($(agent_id), $(user_id),$(user_name), $(message_text), $(message_rich), false) RETURNING messages_id
'''
@nlu_router.route("/nlu_router/operation3", methods=['POST'])
def operation3():
    try:
        data=request.get_json()
        
        message=models.Message(
            agent_id=data['agent_id'],
            user_id=data['user_id'],
            user_name=data['user_name'],
            message_text=data['message_text'],
            message_rich=data['message_rich'],
            user_message_ind=False,
        )

        db.session.add(message)
        db.session.commit()

        return jsonify([{"messages_id": str(message.messages_id)}])
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
INSERT INTO nlu_log(ip_address, query, event_type, event_data)
values($(ip_address), $(query), $(event_type), $(event_data))
'''
@nlu_router.route("/nlu_router/operation4", methods=['POST'])
def operation4():
    try:
        data=request.get_json()
        
        db.session.add(models.NluLog(
            ip_address=data['ip_address'],
            query=data['query'],
            event_type=data['event_type'],
            event_data=data['event_data'],
        ))
        db.session.commit()

        return utils.result('success', 'Inserted NLU log')
    except Exception as e:
        db.session.rollback()
        return(str(e))

'''
SELECT agents.endpoint_enabled as agent_endpoint, agents.endpoint_url, 
agents.basic_auth_username, agents.basic_auth_password, intents.endpoint_enabled 
as intent_endpoint, intents.intent_id, intents.intent_name 
FROM agents, intents 
WHERE agents.agent_name=$2 and intents.intent_name=$1 and 
intents.agent_id=agents.agent_id
'''
@nlu_router.route("/nlu_router/operation5", methods=['GET'])
def operation5():
    try:
        intent_name=request.args.get('intent_name')
        project_name=request.args.get('project_name')

        agents=models.Agent
        intents=models.Intent

        results=db.session.query(
            agents.endpoint_enabled.label('agent_endpoint'),
            agents.endpoint_url,
            agents.basic_auth_username,
            agents.basic_auth_password,
            intents.endpoint_enabled.label('intent_endpoint'),
            intents.intent_id,
            intents.intent_name
        ).filter(
            agents.agent_name==project_name,
            intents.intent_name==intent_name,
            intents.agent_id==agents.agent_id
        ).all()

        return jsonify([{
            'agent_endpoint': e[0],
            'endpoint_url': e[1],
            'basic_auth_username': e[2],
            'basic_auth_password': e[3],
            'intent_endpoint': e[4],
            'intent_id': e[5],
            'intent_name': e[6]
        } for e in results])
    except Exception as e:
        return(str(e))


'''
SELECT responses.response_text 
FROM responses, intents 
WHERE responses.intent_id = intents.intent_id and 
intents.intent_id = $1 order by random() LIMIT 1'
'''
@nlu_router.route("/nlu_router/operation6", methods=['GET'])
def operation6():
    try:
        intent_id=request.args.get('intent_id')
        
        data=models.Response.query.join(models.Intent,
             models.Response.intent_id==models.Intent.intent_id)\
            .filter(models.Intent.intent_id==intent_id)\
            .order_by(func.random()).limit(1)\
            .with_entities(models.Response.response_text).all()

        result = None if len(data)==0 else data[0][0]

        return jsonify({'response_text': result})
    except Exception as e:
        return(str(e))
    