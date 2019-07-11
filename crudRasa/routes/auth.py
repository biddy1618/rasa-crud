from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils


auth=Blueprint('auth', __name__)


'''
SELECT * FROM agents WHERE agent_name = $1 AND client_secret_key=$2
'''
@auth.route('/auth/operation1', methods=['POST'])
def operation1():
    try:
        data=request.get_json()
        result=models.Agent.query.filter_by(
            agent_name=data['agent_name'],
            client_secret_key=data['client_secret_key']
        ).one()
        return jsonify(result.serialize())
    except Exception as e:
        return(str(e))