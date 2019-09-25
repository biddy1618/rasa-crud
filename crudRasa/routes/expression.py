from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

expression=Blueprint('expression', __name__)

@expression.route("/intent_expressions", methods=['GET'])
def intentExpressionQuery():
    try:
        data=request.args.get('intent_ids')
        params=utils.makeList(data)
        expressions=models.Expression.query.filter(\
            models.Expression.intent_id.in_(params)).all()
        return jsonify([e.serialize() for e in expressions])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@expression.route("/intents/<intent_id>/expressions", methods=['GET'])
def intentExpressions(intent_id):
    try:
        expressions=models.Expression.query.filter_by(\
            intent_id=intent_id).all()
        return jsonify([e.serialize() for e in expressions])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

@expression.route("/expressions/<expression_id>", methods=['GET', 'PUT', 'DELETE'])
def expressionID(expression_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            expression=db.session.query(models.Expression)\
                .filter_by(expression_id=expression_id).first_or_404()
            data['lemmatized_text'] = utils.lemmatize(data['expression_text'])
            expression.update(data)
            db.session.commit()
            return utils.result('success', 'Updated expression')
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)
    
    if request.method=='DELETE':
        try:
            db.session.query(models.Expression)\
                .filter_by(expression_id=expression_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed expression {expression_id}')
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)

    try:
        expression=models.Expression.query\
            .filter_by(expression_id=expression_id).first_or_404()
        return jsonify(expression.serialize())
    except Exception as e:
	    return(f"Internal server error: {str(e)}", 500)


@expression.route('/expressions', methods=['POST', 'GET'])
def createExpression():
    if request.method=='GET':
        try:
            query = request.args.get('expression')
            lemmatized_text = utils.lemmatize(query)

            expressions=models.Expression.query.filter_by(
                lemmatized_text=lemmatized_text
            ).all()

            intents=models.Intent.query.filter(
                models.Intent.intent_id.in_((e.intent_id for e in expressions))
            ).all()

            return jsonify([i.serialize() for i in intents])

        except Exception as e:
            return(f"Internal server error: {str(e)}", 500)

    else:
        try:
            data=request.get_json()

            expression=models.Expression(
                intent_id=data['intent_id'],
                expression_text=data['expression_text'],
                lemmatized_text=utils.lemmatize(
                    data['expression_text']
                )
            )
            db.session.add(expression)
            db.session.commit()
            return jsonify([expression.serialize()])
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)
