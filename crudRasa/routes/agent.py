from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

agent=Blueprint('agent', __name__)

@agent.route("/agents", methods=['GET', 'POST'])
def agents():
    if request.method=='POST':
        try:
            data=request.get_json()
            db.session.add(models\
                .Agent(agent_name=data['agent_name']))
            db.session.commit()
            return utils.result('success', 'Inserted')
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)
    
    try:
        agents=models.Agent.query.all()
        return  jsonify([a.serialize() for a in agents])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@agent.route("/agents/<agent_id>", methods=['GET', 'PUT', 'DELETE'])
def agentsID(agent_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            agent=db.session.query(models.Agent)\
                .filter_by(agent_id=agent_id).first_or_404()
            agent.update(data)
            db.session.commit()
            return utils.result('success', 'Updated agent')
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)
    
    if request.method=='DELETE':
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
            return(f"Internal server error: {str(e)}", 500)
    try:
        agent=models.Agent.query\
            .filter_by(agent_id=agent_id).first_or_404()
        return jsonify(agent.serialize())
    except Exception as e:
	    return(f"Internal server error: {str(e)}", 500)


@agent.route('/agentStory', methods=['POST'])
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
        return(f"Internal server error: {str(e)}", 500)