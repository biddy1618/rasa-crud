from flask import request, jsonify, Blueprint

import utils
from app import db
from db import models

expression=Blueprint('expression', __name__)

@expression.route("/intent_expressions", methods=['GET'])
def intentExpressionQuery():
    try:
        data=request.query.intent_ids
        print(data)
        print(type(data))
        expressions=models.Expression.query.filter(\
            models.Expression.intent_id.in_(data)).all()
        return jsonify([e.serialize() for e in expressions])
    except Exception as e:
        return(str(e))

@expression.route("/intents/<intent_id>/expressions", methods=['GET'])
def intentExpressions(intent_id):
    try:
        expressions=models.Expression.query.filter_by(\
            intent_id=intent_id).all()
        return jsonify([e.serialize() for e in expressions])
    except Exception as e:
        return(str(e))

@expression.route("/expressions/<expression_id>", methods=['GET', 'PUT', 'DELETE'])
def expressionID(expression_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            expression=db.session.query(models.Expression)\
                .filter_by(expression_id=expression_id).first_or_404()
            data['expression_lemmatized'] = utils.lemmatize(data['expression_text'])
            expression.update(data)
            db.session.commit()
            return utils.result('success', 'Updated expression')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method=='DELETE':
        try:
            db.session.query(models.Expression)\
                .filter_by(expression_id=expression_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed intent {expression_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))

    try:
        expression=models.Expression.query\
            .filter_by(expression_id=expression_id).first_or_404()
        return jsonify(expression.serialize())
    except Exception as e:
	    return(str(e))


@expression.route('/expressions', methods=['POST'])
def createExpression():
    try:
        data=request.get_json()
        db.session.add(models.Expression(
            intent_id=data['intent_id'],
            expression_text=data['expression_text'],
            expression_lemmatized=utils.lemmatize(
                data['expression_text']
            )
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))