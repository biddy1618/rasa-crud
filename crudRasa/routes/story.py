from flask import request, jsonify, Blueprint

from app import db, func
from orm import models, utils

import json


story=Blueprint('story', __name__)

@story.route('/story/<intent_id>', methods=['POST', 'GET', 'DELETE'])
def getParents(intent_id):
    if request.method=='POST':
        try:
            data=request.get_json()
            intentStory=models.IntentStory(
                intent_id=intent_id,
                parent_id=data['parent_id'],
            )
            db.session.add(intentStory)
            db.session.commit()
            return jsonify([intentStory.serialize()])
        except Exception as e:
            db.session.rollback()
            return(str(e))
    
    if request.method=='DELETE':
        try:
            data=request.get_json()
            db.session.query(models.IntentStory)\
                .filter_by(intent_id=intent_id, parent_id=data['parent_id']).delete()
            db.session.commit()
            return utils.result('success', f'Removed parent {data["parent_id"]}')
        except Exception as e:
            db.session.rollback()
            return(str(e))

    try:
        parents=db.session.query(models.IntentStory, models.Intent)\
            .filter(models.IntentStory.intent_id==intent_id)\
            .filter(models.IntentStory.parent_id==models.Intent.intent_id)\
            .with_entities(
                models.IntentStory.intent_id,
                models.IntentStory.parent_id,
                models.Intent.intent_name,
            ).all()

        # query=("SELECT t1.intent_id, t1.parent_id, t2.intent_name "
        #         "from intent_story t1 join intents t2 on t1.parent_id = t2.intent_id "
        #         "where t1.intent_id=:intent_id")
        # parents = db.session.execute(query, {'intent_id': intent_id})
        return jsonify([{
            'intent_id': e[0],
            'parent_id': e[1],
            'parent_name': e[2],
        } for e in parents])
    except Exception as e:
	    return(str(e))