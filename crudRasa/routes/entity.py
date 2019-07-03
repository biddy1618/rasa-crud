from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

entity = Blueprint('entity', __name__)

@entity.route('/entities/agent/<agent_id>', methods=['GET'])
def entityAgent(agent_id):
    try:
        entities=models.Entity.query.\
            filter_by(agent_id=agent_id).all()
        return jsonify([e.serialize() for e in entities])
    except Exception as e:
        return(str(e))

@entity.route('/entities/<entity_id>', methods=['GET', 'PUT', 'DELETE'])
def entityID(entity_id):
    if request.method=='PUT':
        try:
            data=request.get_json()
            data.pop('agent', None)
            entity=db.session.query(models.Entity)\
                .filter_by(entity_id=entity_id).first_or_404()
            entity.update(data)
            db.session.commit()
            return utils.result('success', 'Updated agent')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    if request.method=='DELETE':
        try:
            db.session.query(models.Entity)\
                .filter_by(entity_id=entity_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed entity {entity_id}')
        except Exception as e:
            return(str(e))
    try:
        entity=models.Entity.query.\
            filter_by(entity_id=entity_id).first_or_404()
        return jsonify(entity.serialize())
    except Exception as e:
        return(str(e))

@entity.route('/entities', methods=['GET', 'POST'])
def entityAll():
    if request.method=='POST':
        try:
            data=request.get_json()
            db.session.add(models.Entity(
                agent_id=data['agent']['agent_id'],
                entity_name=data['entity_name'],
                slot_data_type=data['slot_data_type']
            ))
            db.session.commit()
            return utils.result('success', 'Inserted')
        except Exception as e:
            db.session.rollback()
            return(str(e))
    try:
        entities = models.Entity.query.all()
        return jsonify([e.serialize() for e in entities])
    except Exception as e:
        return(str(e))
