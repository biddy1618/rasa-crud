from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

synonym=Blueprint('synonym', __name__)

@synonym.route('/agent/<agent_id>/synonyms', methods=['GET'])
def synonymAgent(agent_id):
    try:
        synonyms=models.Synonym.query.filter_by(\
            agent_id=agent_id).all()
        return jsonify([s.serialize() for s in synonyms])
    except Exception as e:
        return(str(e))

@synonym.route('/synonyms/<synonym_id>', methods=['GET', 'DELETE'])
def synonymID(synonym_id):
    if request.method=='DELETE':
        try:
            db.session.query(models.Synonym)\
                .filter_by(synonym_id=synonym_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed synonym {synonym_id}')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    try:
        synonym=models.Synonym.query.filter_by(\
            synonym_id=synonym_id).first_or_404()
        return jsonify(synonym.serialize())
    except Exception as e:
        return(str(e))

@synonym.route('/synonyms', methods=['POST'])
def createSynonym():
    try:
        data=request.get_json()
        db.session.add(models.Synonym(
            synonym_reference=data['synonym_reference'],
            agent_id=data['agent_id']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(str(e))
