from flask import request, jsonify, Blueprint

from app import db
from models import models, utils

regex=Blueprint('regex', __name__)

@regex.route('/agent/<agent_id>/regex', methods=['GET'])
def regexAgent(agent_id):
    try:
        regexes=models.Regex.query.filter_by(\
            agent_id=agent_id).all()
        return jsonify([r.serialize() for r in regexes])
    except Exception as e:
        return(str(e))

@regex.route('/regex/<regex_id>', methods=['GET', 'PUT', 'DELETE'])
def regexID(regex_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            regex=db.session.query(models.Regex)\
                .filter_by(regex_id=regex_id).first_or_404()
            regex.update(data)
            db.session.commit()
            return utils.result('success', 'Updated regex')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method=='DELETE':
        try:
            db.session.query(models.Regex)\
                .filter_by(regex_id=regex_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed intent {regex_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))

    try:
        regex=models.Regex.query\
            .filter_by(regex_id=regex_id).first_or_404()
        return jsonify(regex.serialize())
    except Exception as e:
	    return(str(e))

@regex.route('/regex', methods=['POST'])
def createRegex():
    try:
        data=request.get_json()
        db.session.add(models.Regex(
            regex_name=data['regex_name'],
            regex_pattern=data['regex_pattern'],
            agent_id=data['agent_id']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))