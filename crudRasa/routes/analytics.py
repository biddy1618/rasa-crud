from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

analytics=Blueprint('analytics', __name__)

'''
SELECT count(t.*)
FROM (
    SELECT sender_id, DATE(dateandtime) 
    from rasa_ui.analytics 
    GROUP BY sender_id, DATE(dateandtime)
) t

SELECT t.date, count(t.*)
FROM (
    SELECT DATE(dateandtime) as date
    from rasa_ui.analytics
    GROUP BY sender_id, DATE(dateandtime)
) t 
GROUP BY t.date;
'''
@analytics.route("/analytics/sessions/1", methods=['GET'])
def session1():
    try:
        days=request.args.get('days')
        
        query1=('SELECT count(t.*) as cnt '
            'FROM ('
                'SELECT sender_id, DATE(dateandtime) '
                'from rasa_ui.analytics '
                'where DATE(dateandtime) >= CURRENT_DATE - :days '
                'GROUP BY sender_id, DATE(dateandtime)'
            ') t')

        query2=('SELECT t.date, count(t.*) '
        'FROM ('
            'SELECT DATE(dateandtime) as date '
            'from rasa_ui.analytics '
            'where DATE(dateandtime) >= CURRENT_DATE - :days '
            'GROUP BY sender_id, DATE(dateandtime)'
        ') t '
        'GROUP BY t.date')

        result1=db.session.execute(query1, {'days': int(days)}).fetchone()
        result2=db.session.execute(query2, {'days': int(days)}).fetchall()
        
        return jsonify(
            {
                'sessionCount': int(result1[0]),
                'dates': [models.Helper.serializeStatic(e) for e in result2]
            })
    except Exception as e:
        return(str(e))

'''
SELECT avg(t.cnt) 
FROM (
    SELECT sender_id, DATE(dateandtime), count(*) as cnt 
    from rasa_ui.analytics 
    GROUP BY sender_id, DATE(dateandtime)
) t

SELECT t.date, avg(t.cnt)
FROM (
    SELECT DATE(dateandtime) as date, count(*) as cnt
    from rasa_ui.analytics
    GROUP BY sender_id, DATE(dateandtime)
) t 
GROUP BY t.date
'''
@analytics.route("/analytics/sessions/2", methods=['GET'])
def session2():
    try:
        days=request.args.get('days')
        
        query1=('SELECT avg(t.cnt) as queryPerSession '
        'FROM ('
            'SELECT count(*) as cnt '
            'from rasa_ui.analytics '
            'where DATE(dateandtime) >= CURRENT_DATE - :days '
            'GROUP BY sender_id, DATE(dateandtime)'
        ') t')

        query2=('SELECT t.date, avg(t.cnt) '
        'FROM ('
            'SELECT DATE(dateandtime) as date, count(*) as cnt '
            'from rasa_ui.analytics '
            'where DATE(dateandtime) >= CURRENT_DATE - :days '
            'GROUP BY sender_id, DATE(dateandtime)'
        ') t '
        'GROUP BY t.date')

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


'''
SELECT intent_name, 
    count(*) as cnt, 
    count(DISTINCT(sender_id, DATE(dateandtime))) as sessions, 
    avg(response_time) as avgRespTime
FROM rasa_ui.analytics
WHERE DATE(dateandtime) >= CURRENT_DATE - :days
GROUP BY intent_name
'''
@analytics.route("/analytics/intents/1", methods=['GET'])
def intent1():
    try:
        days=request.args.get('days')
        
        query=('SELECT intent_name, '
            'count(*) as cnt, '
            'count(DISTINCT(sender_id, DATE(dateandtime))) as sessions, '
            'avg(response_time) as avgRespTime '
        'FROM rasa_ui.analytics '
        'WHERE DATE(dateandtime) >= CURRENT_DATE - :days '
        'GROUP BY intent_name')

        result=db.session.execute(query, {'days': int(days)}).fetchall()
        
        return jsonify({'intents': [models.Helper.serializeStatic(e) for e in result]})
    except Exception as e:
        return(str(e))


'''
SELECT sender_id as userid, 
    DATE(dateandtime) as chatdate, 
    COUNT(DISTINCT intent_name) as intentions
FROM rasa_ui.analytics
GROUP BY sender_id, DATE(dateandtime)
'''
@analytics.route("/analytics/intents/2", methods=['GET'])
def intent2():
    try:
        itemsPerPage=request.args.get('itemsPerPage')
        page=request.args.get('page')

        itemsPerPage=0 if itemsPerPage is None else int(itemsPerPage)
        page=1 if page is None else int(page)

        
        query=('SELECT sender_id as userID, '
                'DATE(dateandtime) as chatDate, '
                'COUNT(DISTINCT intent_name) as intentions '
            'FROM rasa_ui.analytics '
            'GROUP BY sender_id, DATE(dateandtime) '
            'ORDER BY DATE(dateandtime) desc '
            'LIMIT :limit OFFSET :offset')

        results=db.session.execute(query, {
            'limit': itemsPerPage,
            'offset': (page-1)*itemsPerPage
        }).fetchall()

        return jsonify([models.Helper.serializeStatic(e) for e in results])
    except Exception as e:
        return(str(e))

