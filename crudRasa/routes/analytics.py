from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

analytics=Blueprint('analytics', __name__)


# [Insights] Enpoint for session count, and session info by day
@analytics.route("/analytics/sessions/1", methods=['GET'])
def session1():
    try:
        days=request.args.get('days')
        
        query1=('SELECT COUNT(DISTINCT session_id) '
            'FROM rasa_ui.analytics '
            'WHERE DATE(dateandtime) >= CURRENT_DATE - :days')

        
        query2=('SELECT t.date, sum(t.cnt) as count '
            'FROM ('
                'SELECT DATE(dateandtime) as date, '
                'session_id, count(*) as cnt '
                'from rasa_ui.analytics '
                'where DATE(dateandtime) >= CURRENT_DATE - :days '
                'GROUP BY session_id, DATE(dateandtime)'
            ') t '
            'GROUP BY t.date '
            'ORDER BY t.date')

        result1=db.session.execute(query1, {'days': int(days)}).fetchone()
        result2=db.session.execute(query2, {'days': int(days)}).fetchall()
        
        return jsonify(
            {
                'sessionCount': int(result1[0]),
                'dates': [models.Helper.serializeStatic(e) for e in result2]
            })
    except Exception as e:
        return(str(e))


# [Insights] Endpoint for queries per session and queries info per day
@analytics.route("/analytics/sessions/2", methods=['GET'])
def session2():
    try:
        days=request.args.get('days')
        
        query1=('SELECT avg(t.cnt) as queryPerSession '
            'FROM ('
                'SELECT count(*) as cnt '
                'FROM rasa_ui.analytics '
                'where DATE(dateandtime) >= CURRENT_DATE - :days '
                'GROUP BY session_id'
            ') t')

        query2=('SELECT t.date, avg(t.cnt) '
            'FROM ('
                'SELECT DATE(dateandtime) as date, count(*) as cnt '
                'from rasa_ui.analytics '
                'where DATE(dateandtime) >= CURRENT_DATE - :days '
                'GROUP BY session_id, DATE(dateandtime)'
            ') t '
            'GROUP BY t.date '
            'ORDER BY t.date')

        result1=db.session.execute(query1, {'days': int(days)}).fetchone()
        result2=db.session.execute(query2, {'days': int(days)}).fetchall()
        
        queriesPerSession=.0 if result1[0] is None else float(result1[0])
        
        return jsonify(
            {
                'queryPerSession': queriesPerSession,
                'dates': [models.Helper.serializeStatic(e) for e in result2]
            })
    except Exception as e:
        return(str(e))


# [Conversations] Endpoint for single session details
@analytics.route("/analytics/sessions/3", methods=['GET'])
def session3():
    try:
        sessionId=request.args.get('session_id')
        
        query=('SELECT sender_id, dateandtime, user_message, '
                'bot_message, intent_name, response_time '
            'FROM rasa_ui.analytics WHERE session_id = :sessionId '
            'ORDER BY dateandtime')

        result=db.session.execute(query, {'sessionId': sessionId}).fetchall()
        
        return jsonify({
                'messages': [models.Helper.serializeStatic(e) for e in result]
            })
    except Exception as e:
        return(str(e))


# [Insights] Endpoint for intents used info
@analytics.route("/analytics/intents/1", methods=['GET'])
def intent1():
    try:
        days=request.args.get('days')
        itemsPerPage=request.args.get('itemsPerPage')
        page=request.args.get('page')

        itemsPerPage=0 if itemsPerPage is None else int(itemsPerPage)
        page=1 if page is None else int(page)
        
        query=('SELECT intent_name, '
                'count(*) as cnt, '
                'count(DISTINCT session_id) as sessions, '
                'avg(response_time) as avgRespTime '
            'FROM rasa_ui.analytics '
            'WHERE DATE(dateandtime) >= CURRENT_DATE - :days '
            'GROUP BY intent_name '
            'LIMIT :limit OFFSET :offset')

        result=db.session.execute(query, {
            'days': int(days),
            'limit': itemsPerPage,
            'offset': (page-1)*itemsPerPage
        }).fetchall()
        
        return jsonify({'intents': [models.Helper.serializeStatic(e) for e in result]})
    except Exception as e:
        return(str(e))


# [Conversations] Endpoint for conversations info
@analytics.route("/analytics/intents/2", methods=['GET'])
def intent2():
    try:
        itemsPerPage=request.args.get('itemsPerPage')
        page=request.args.get('page')

        itemsPerPage=0 if itemsPerPage is None else int(itemsPerPage)
        page=1 if page is None else int(page)

        query=('SELECT t1.sender_id as userID, '
                't1.dateandtime as chatDate, '
                't1.session_id, t2.cnt as intentions, '
                't3.not_found '
            'FROM (SELECT sender_id, dateandtime, session_id, row_number() '
                'OVER(PARTITION BY session_id ORDER BY dateandtime) AS rn '
                'FROM rasa_ui.analytics) t1 '
            'JOIN ('
                'SELECT session_id, count(*) cnt FROM rasa_ui.analytics '
                'GROUP BY session_id) t2 '
            'ON t1.session_id = t2.session_id LEFT JOIN ('
                'SELECT DISTINCT session_id, TRUE as not_found '
                'FROM rasa_ui.analytics '
                'WHERE intent_name = \'default\''
            ') t3 ON t1.session_id = t3.session_id '
            'WHERE t1.rn = 1 '
            'ORDER BY t1.dateandtime desc '
            'LIMIT :limit OFFSET :offset')

        results=db.session.execute(query, {
            'limit': itemsPerPage,
            'offset': (page-1)*itemsPerPage
        }).fetchall()

        return jsonify([models.Helper.serializeStatic(e) for e in results])
    except Exception as e:
        return(str(e))

