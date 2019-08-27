from flask import request, jsonify, Blueprint

from app import db, func
from orm import models, utils

import json


response=Blueprint('response', __name__)

@response.route('/actionresponse/<action_id>', methods=['GET'])
def responseActionID(action_id):
    try:
        responses=models.Response.query\
            .filter_by(action_id=action_id).all()
        return jsonify([r.serialize() for r in responses])
    except Exception as e:
        return(str(e))

@response.route('/actionresponse', methods=['POST'])
def responseAction():
    try:
        data=request.get_json()

        print('dauren is the loh')
        response=models.Response(
            intent_id=data['intent_id'],
            action_id=data['action_id'],
            response_text=data['response_text'],
            response_type=data['response_type'],
            buttons_info=None if data['buttons_info'] is None else data['buttons_info'],          
        )
        db.session.add(response)
        print('dauren is the best')
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))

@response.route('/response/<intent_id>', methods=['GET'])
def responseIntentID(intent_id):
    try:
        responses=models.Response.query\
            .filter_by(intent_id=intent_id).all()
        return jsonify([r.serialize() for r in responses])
    except Exception as e:
        return(str(e))

@response.route('/response', methods=['POST'])
def responseIntent():
    try:
        data=request.get_json()
        db.session.add(models.Response(
            intent_id=data['intent_id'],
            action_id=data['action_id'],
            response_text=data['response_text'],
            response_type=data['response_type']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))

@response.route('/response/<response_id>', methods=['DELETE'])
def responseIntentRemove(response_id):
    try:
        db.session.query(models.Response)\
            .filter_by(response_id=response_id).delete()
        db.session.commit()
        return utils.result('success', f'Removed response {response_id}')
    except Exception as e:
        db.session.rollback()
        return(str(e))

@response.route('/rndmresponse', methods=['GET'])
def responseIntentRandom():
    try:
        param=request.args.get('intent_name')

        data=models.Response.query.join(models.Intent,
             models.Response.intent_id==models.Intent.intent_id)\
            .filter(models.Intent.intent_name==param)\
            .order_by(func.random()).limit(1)\
            .with_entities(models.Response.response_text).all()
        result = None if len(data)==0 else data[0][0]

        return jsonify({'response_text': result})
    except Exception as e:
        return(str(e))

@response.route('/action_responses', methods=['GET'])
def responseActions():
    try:
        '''
        Get URL-encoded parameters that are given in the form
        of the string list "...?a=i1,i2,i3...".

        makeList returns python list of strings of the parameters.

        The query combines two tables, thus query generated from
        the ORM model is somehow complex, using join, and filters.
        
        Serialization is customized as well, since the result
        of the query combines fields from the two models.
        '''
        params=request.args.get('action_ids')
        params=utils.makeList(params)


        data=models.Response.query.join(models.Action, 
                models.Response.action_id==models.Action.action_id)\
            .filter(models.Response.action_id.in_(params))\
            .add_columns(models.Action.action_name).all()
        
        results=[item[0].serialize() for item in data]
        
        for i, item in enumerate(results):
            item.update({'action_name': data[i][1]})
        
        return jsonify(results)
    except Exception as e:
        return(str(e))


