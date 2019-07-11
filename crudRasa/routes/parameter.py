from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

parameter=Blueprint('parameter', __name__)

@parameter.route('/expression_parameters', methods=['GET'])
def parameterExpressionTrain():
    try:
        data=request.args.get('expression_ids')
        params=utils.makeList(data)
        parameters=db.session.query(models.t_expression_parameters)\
            .filter(models.t_expression_parameters\
                .c.expression_id.in_(params)).all()
        return jsonify([models.Helper\
            .serializeStatic(p) for p in parameters])
    except Exception as e:
        return(str(e))

@parameter.route('/expressions/<expression_id>/parameters', methods=['GET'])
def parameterExpression(expression_id):
    try:
        parameters=db.session.query(models.t_expression_parameters)\
            .filter(models.t_expression_parameters\
                .c.expression_id==expression_id).all()
        return jsonify([models.Helper\
            .serializeStatic(p) for p in parameters])
    except Exception as e:
        reutrn(str(e))

@parameter.route('/parameters/<parameter_id>', methods=['GET', 'PUT', 'DELETE'])
def parameterID(parameter_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            parameter=db.session.query(models.Parameter)\
                .filter_by(parameter_id=parameter_id).first_or_404()
            parameter.entity_id=data['entity_id']
            db.session.commit()
            return utils.result('success', 'Updated parameter')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method=='DELETE':
        try:
            db.session.query(models.Parameter)\
                .filter_by(parameter_id=parameter_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed parameter {parameter_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))

    try:
        parameter=models.Parameter.query\
            .filter_by(parameter_id=parameter_id).first_or_404()
        return jsonify(parameter.serialize())
    except Exception as e:
	    return(str(e))

@parameter.route('/intent/<intent_id>/parameters', methods=['GET'])
def parameterIntent(intent_id):
    try:
        parameters=db.session.query(models.t_expression_parameters)\
            .filter_by(intent_id=intent_id).all()
        return jsonify([p.serialize() for p in parameters])
    except Exception as e:
        return(str(e))

@parameter.route('/parameters', methods=['POST'])
def parameters():
    try:
        data=request.get_json()
        if 'entity_id' not in data:
            data['entity_id']=None

        db.session.add(models.Parameter(
            expression_id=data['expression_id'],
            parameter_end=data['parameter_end'],
            parameter_start=data['parameter_start'],
            parameter_value=data['parameter_value'],
            entity_id=data['entity_id'],
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))