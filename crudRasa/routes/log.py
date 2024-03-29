from flask import request, jsonify, Blueprint

from app import db, func
from orm import models, utils


log=Blueprint('log', __name__)

@log.route('/nlu_log/<query>', methods=['GET'])
def nluLog(query):
    try:
        data=db.session.query(models.NluLog)\
            .filter_by(event_type=query)\
            .order_by(models.NluLog.timestamp.desc())\
            .limit(100).all()
        return jsonify([l.serialize() for l in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/intent_usage_by_day', methods=['GET'])
def intentUsageByDay():
    try:
        data=db.session.query(models.t_intent_usage_by_day).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/intent_usage_total', methods=['GET'])
def intentUsageTotal():
    try:
        data=db.session.query(models.t_intent_usage_total).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/request_usage_total', methods=['GET'])
def requestUsageTotal():
    try:
        data=db.session.query(models.t_request_usage_total).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)


@log.route('/avg_intent_usage_by_day', methods=['GET'])
def avgIntentUsageByDay():
    try:
        data=db.session.query(
            func.round(\
            func.avg(models.t_intent_usage_by_day.c.count))\
            .label('avg')).first_or_404()
        return jsonify({'avg': 0.0 if data[0] is None else data[0]})
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/nlu_parse_log/<agent_id>', methods=['GET'])
def nluParseLog(agent_id):
    '''
    select * from nlu_parse_log where agent_id = $1 order by timestamp desc
    '''
    try:
        data=models.NluParseLog.query\
            .filter_by(agent_id=agent_id)\
            .order_by(models.NluParseLog.timestamp.desc())\
            .all()
        return jsonify([l.serialize() for l in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/agentByIntentConfidencePct/<agent_id>', methods=['GET'])
def agentByIntentConfidencePct(agent_id):
    '''
    SELECT COUNT(*),intent_confidence_pct, agents.agent_id, agents.agent_name FROM nlu_parse_log, agents, messages
    WHERE messages.agent_id = agents.agent_id AND messages.messages_id=nlu_parse_log.messages_id
    AND agents.agent_id=$1 GROUP BY intent_confidence_pct, agents.agent_id, agents.agent_name
    '''
    try:
        agents=models.Agent
        nluParseLog=models.NluParseLog
        messages=models.Message

        results=db.session.query(func.count('*'), 
            nluParseLog.intent_confidence_pct, 
            agents.agent_id, 
            agents.agent_name
        ).filter(
            messages.agent_id==agents.agent_id,
            messages.messages_id==nluParseLog.messages_id,
            agents.agent_id==agent_id
        ).group_by(
            nluParseLog.intent_confidence_pct,
            agents.agent_id,
            agents.agent_name
        ).all()

        return jsonify([{
            'count': e[0],
            'intent_confidence_pct': e[1],
            'agent_id': e[2],
            'agent_name': e[3]
        } for e in results])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/intentsMostUsed/<agent_id>', methods=['GET'])
def intentsMostUsed(agent_id):
    try:
        data=db.session.query(models.t_intents_most_used)\
            .filter_by(agent_id=agent_id).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/avgNluResponseTimesLast30Days', methods=['GET'])
def avgNluResponseTimesLast30Days():
    try:
        data=db.session.query(models.t_avg_nlu_response_times_30_days).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)
    
@log.route('/avgUserResponseTimesLast30Days', methods=['GET'])
def avgUserResponseTimesLast30Days():
    try:
        data=db.session.query(models.t_avg_user_response_times_30_days).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)
    
@log.route('/activeUserCountLast12Months', methods=['GET'])
def activeUserCountLast12Months():
    try:
        data=db.session.query(models.t_active_user_count_12_months).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@log.route('/activeUserCountLast30Days', methods=['GET'])
def activeUserCountLast30Days():
    try:
        data=db.session.query(models.t_active_user_count_30_days).all()
        return jsonify([models.Helper\
            .serializeStatic(d) for d in data])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)
