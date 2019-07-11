from flask import request, jsonify, Blueprint

from app import db, func
from orm import models, utils


messages=Blueprint('messages', __name__)


'''
SELECT user_id,user_name, MAX(timestamp) as recent_active 
FROM messages WHERE agent_id=$1 GROUP BY user_id,user_name 
ORDER BY recent_active DESC LIMIT 9
'''
@messages.route('/messages/operation1', methods=['GET'])
def operation1():
    try:
        agent_id=request.args.get('agent_id')

        results = db.session.query(
            models.Message.user_id, 
            models.Message.user_name, 
            func.max(models.Message.timestamp).label('recent_active')
        ).group_by(
            models.Message.user_id, 
            models.Message.user_name
        ).filter(models.Message.agent_id==agent_id)\
            .order_by(func.max(models.Message.timestamp).desc())\
            .limit(9).all()
        '''
        for r in results1:
            print(r)
        
        query=("SELECT user_id,user_name, MAX(timestamp) as recent_active "
                "FROM messages WHERE agent_id=:agent_id GROUP BY user_id,user_name "
                "ORDER BY recent_active DESC LIMIT 9")
        results2 = db.session.execute(query, {'agent_id': agent_id})
        for r in results2:
            print(r)
        '''
        return jsonify([{
            'user_id': e[0],
            'user_name': e[1],
            'recent_active': e[2],
        } for e in results])
        
    except Exception as e:
        return(str(e))


'''
SELECT COUNT(DISTINCT user_id) FROM messages_expressions 
WHERE agent_id=$1 AND user_id IS NOT NULL
'''
@messages.route('/messages/operation2', methods=['GET'])
def operation2():
    try:
        agent_id=request.args.get('agent_id')

        table=models.t_messages_expressions
        
        result=db.session.query(table)\
            .distinct(table.c.user_id)\
            .filter(db.and_(
                table.c.agent_id==agent_id,
                table.c.agent_id!=None)
            ).count()
                
        return jsonify([{'count': result}])        
    except Exception as e:
        return(str(e))


'''
SELECT user_id, MAX(timestamp) AS recent_active
FROM messages_expressions
WHERE agent_id=$1 AND user_id IS NOT NULL
GROUP BY user_id ORDER BY recent_active DESC
LIMIT $2 OFFSET $3
'''
@messages.route('/messages/operation3', methods=['GET'])
def operation3():
    try:
        agent_id=request.args.get('agent_id')
        itemsPerPage=int(request.args.get('itemsPerPage'))
        offset=int(request.args.get('offset'))

        table=models.t_messages_expressions
        
        results=db.session.query(
            table.c.user_id,
            func.max(table.c.timestamp).label('recent_active')
        ).group_by(table.c.user_id).filter(db.and_(
            table.c.agent_id==agent_id,
            table.c.user_id!=None
        )).order_by(func.max(table.c.timestamp).desc())\
            .limit(itemsPerPage).offset(offset).all()
        
        return jsonify([{
            'user_id': e[0], 
            'user_id': e[1]
            } for e in results])
    except Exception as e:
        return(str(e))


'''
SELECT 
    (SELECT count(messages_id) FROM messages_expressions
    WHERE agent_id=$1 AND user_id=$2 AND intent_id IS NOT NULL
    AND user_name = 'user') as intentsCount,

    (SELECT count(messages_id) FROM messages_expressions
    WHERE agent_id=$1 AND user_id=$2 AND intent_id IS NULL
    AND user_name = 'user') as noMatchCount
'''
@messages.route('/messages/operation4', methods=['GET'])
def operation4():
    try:
        agent_id=request.args.get('agent_id')
        user_id=request.args.get('user_id')

        table=models.t_messages_expressions

        # query=("SELECT (SELECT count(messages_id) FROM messages_expressions "
        #         "WHERE agent_id=:agent_id AND user_id=:user_id AND intent_id IS NOT NULL "
        #         "AND user_name = 'user') as intentsCount, "
        #         "(SELECT count(messages_id) FROM messages_expressions "
        #         "WHERE agent_id=:agent_id AND user_id=:user_id AND intent_id IS NULL "
        #         "AND user_name = 'user') as noMatchCount ")
        # results2 = db.session.execute(query, {'agent_id': agent_id, 'user_id': user_id})
        # for r in results2:
        #     print(r)

        intentsCount=db.session.query(table).filter(db.and_(
            table.c.agent_id==agent_id,
            table.c.user_id==user_id,
            table.c.intent_id!=None,
            table.c.user_name=='user'
            )).count()
        
        noMatchCount=db.session.query(table).filter(db.and_(
            table.c.agent_id==agent_id,
            table.c.user_id==user_id,
            table.c.intent_id==None,
            table.c.user_name=='user'
            )).count()
        
        return jsonify([{
            'intentsCount': intentsCount,
            'noMatchCount': noMatchCount
        }])
    except Exception as e:
        return(str(e))


'''
SELECT * FROM messages_expressions WHERE agent_id=$1 
AND user_id=$2 ORDER BY timestamp ASC
'''
@messages.route('/messages/operation5', methods=['GET'])
def operation5():
    try:
        agent_id=request.args.get('agent_id')
        user_id=request.args.get('user_id')

        table=models.t_messages_expressions

        results = db.session.query(table).filter(
            table.c.agent_id==agent_id,
            table.c.user_id==user_id,
        ).order_by(table.c.timestamp.desc()).all()
        
        return jsonify([models.Helper\
            .serializeStatic(e) for e in results])
    except Exception as e:
        return(str(e))


'''
SELECT * FROM entities_parameters WHERE messages_id=$1
AND entity_id IS NOT NULL AND parameter_id IS NOT NULL
'''
@messages.route('/messages/operation6', methods=['GET'])
def operation6():
    try:
        messages_id=request.args.get('messages_id')
        
        table=models.t_entities_parameters

        results = db.session.query(table).filter(
            table.c.messages_id==messages_id,
            table.c.entity_id!=None,
            table.c.parameter_id!=None,).all()
        
        return jsonify([models.Helper\
            .serializeStatic(e) for e in results])
    except Exception as e:
        return(str(e))


'''
DELETE from messages_entities
WHERE message_id=$1 AND entity_value=$2
'''
@messages.route('/messages/operation7', methods=['DELETE'])
def operation7():
    try:
        message_id=request.args.get('message_id')
        entity_value=request.args.get('entity_value')

        res=db.session.query(models.MessagesEntity).filter(db.and_(
            models.MessagesEntity.message_id==message_id,
            models.MessagesEntity.entity_value==entity_value,
        )).delete()

        db.session.commit()
        return utils.result('success', f'Removed {res} entities')
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
SELECT * FROM entities_parameters
WHERE agent_id=$1 AND parameter_id=$2
'''
@messages.route('/messages/operation8', methods=['GET'])
def operation8():
    try:
        agent_id=request.args.get('agent_id')
        parameter_id=request.args.get('parameter_id')
        
        table=models.t_entities_parameters

        results = db.session.query(table).filter(
            table.c.agent_id==agent_id,
            table.c.parameter_id==parameter_id).all()
        
        return jsonify([models.Helper\
            .serializeStatic(e) for e in results])
    except Exception as e:
        return(str(e))



'''
UPDATE messages_entities SET entity_id=$4, entity_value=$3
WHERE message_id IN ($1:list) AND entity_id=$2
'''
@messages.route('/messages/operation9', methods=['PUT'])
def operation9():
    try:
        data=request.get_json()
        
        entity_id=request.args.get('entity_id')
        messageIds=utils.makeList(request.args.get('messageIds'))
        
        res=db.session.query(models.MessagesEntity).filter(db.and_(
            models.MessagesEntity.message_id.in_(messageIds),
            models.MessagesEntity.entity_id==entity_id,
        )).all()

        for e in res:
            e.update(data)

        db.session.commit()
        return utils.result('success', 'Updated entities')
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
INSERT INTO messages_entities(message_id, entity_id, 
entity_start, entity_end, entity_value, entity_confidence)
values($1, $2, $3, $4, $5, 0)',
'''
@messages.route('/messages/operation10', methods=['POST'])
def operation10():
    try:
        data=request.get_json()

        db.session.add(models.MessagesEntity(
            message_id=data['message_id'],
            entity_id=data['entity_id'],
            entity_start=data['entity_start'],
            entity_end=data['entity_end'],
            entity_value=data['entity_value'],
            entity_confidence=0,
        ))
        db.session.commit()

        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
SELECT * FROM core_parse_log FULL JOIN nlu_parse_log 
ON core_parse_log.messages_id=nlu_parse_log.messages_id 
WHERE core_parse_log.messages_id=$1
'''
@messages.route('/messages/operation11', methods=['GET'])
def operation11():
    try:
        messages_id=request.args.get('messages_id')

        sql_query=("SELECT * FROM core_parse_log FULL JOIN nlu_parse_log "
                    "ON core_parse_log.messages_id=nlu_parse_log.messages_id "
                    "WHERE core_parse_log.messages_id=:messages_id")
        
        results=db.session.execute(sql_query, {'messages_id': messages_id})
        
        results=[{i[0]: i[1] for i in r.items()} for r in results]

        return jsonify(results)
    except Exception as e:
        return(str(e))


'''
SELECT * FROM nlu_parse_log WHERE nlu_parse_log.messages_id=$1
'''
@messages.route('/messages/operation12', methods=['GET'])
def operation12():
    try:
        messages_id=request.args.get('messages_id')
        
        results=models.NluParseLog.query.filter_by(
            messages_id=messages_id
        ).all()

        return jsonify([e.serialize() for e in results])
    except Exception as e:
        return(str(e))


'''
INSERT INTO messages(agent_id, user_id, user_name, message_text, 
message_rich, user_message_ind) values($(agent_id), $(user_id),
$(user_name), $(message_text),$(message_rich), $(user_message_ind))
'''
@messages.route('/messages/operation13', methods=['POST'])
def operation13():
    try:
        data=request.get_json()

        db.session.add(models.Message(
            agent_id=data['agent_id'],
            user_id=data['user_id'],
            user_name=data['user_name'],
            message_text=data['message_text'],
            message_rich=data['message_rich'],
            user_message_ind=data['user_message_ind'],
        ))
        db.session.commit()

        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))


'''
UPDATE messages SET intent_id=$1 WHERE messages_id=$2
'''
@messages.route('/messages/operation14', methods=['PUT'])
def operation14():
    try:
        data=request.get_json()
        messages_id=request.args.get('messages_id')
        
        res=db.session.query(models.Message).filter(
            models.Message.messages_id==messages_id,
        ).all()

        for e in res:
            e.update(data)

        db.session.commit()
        return utils.result('success', 'Updated entities')
    except Exception as e:
        db.session.rollback()
        return(str(e))