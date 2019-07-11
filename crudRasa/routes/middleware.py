from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils


middleware=Blueprint('middleware', __name__)

'''
SELECT agent_id, agent_name, endpoint_enabled, endpoint_url, 
basic_auth_username, basic_auth_password, rasa_core_enabled 
FROM agents WHERE agent_name = $1'
'''
@middleware.route("/middleware/operation1", methods=['GET'])
def operation6():
    try:
        agent_name=request.args.get('agent_name')
        
        data=models.Agent.query.filter_by(agent_name=agent_name)\
            .with_entities(
                models.Agent.agent_id,
                models.Agent.agent_name,
                models.Agent.endpoint_enabled,
                models.Agent.endpoint_url,
                models.Agent.basic_auth_username,
                models.Agent.basic_auth_password,
                models.Agent.rasa_core_enabled
            ).all()
        
        return jsonify([{
            'agent_id': e[0],
            'agent_name': e[1],
            'endpoint_enabled': e[2],
            'endpoint_url': e[3],
            'basic_auth_username': e[4],
            'basic_auth_password': e[5],
            'rasa_core_enabled': e[6],
            } for e in data])
    except Exception as e:
        return(str(e))
    
