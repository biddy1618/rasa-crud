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
            return(f"Internal server error: {str(e)}", 500)
    
    if request.method=='DELETE':
        try:
            data=request.get_json()
            db.session.query(models.IntentStory)\
                .filter_by(intent_id=intent_id, parent_id=data['parent_id']).delete()
            db.session.commit()
            return utils.result('success', f'Removed parent {data["parent_id"]}')
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)

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
	    return(f"Internal server error: {str(e)}", 500)
    
@story.route('/storyFind', methods=['GET'])
def storyList():
    try:
        query=request.args.get('query')
        if query is None:
            results=models.Story.query.with_entities(
                models.Story.story_name, models.Story.story_id
            ).all()
        else:
            query= f'%{query}%'
            results=models.Story.query.with_entities(
                models.Story.story_name, models.Story.story_id
            ).filter(models.Story.story_name.like(query)).all()
        
        return jsonify([models.Helper\
            .serializeStatic(i) for i in results]) 
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)
    

@story.route('/storyGet/<story_id>', methods=['GET'])
def getSory(story_id):
    try:
        story=models.Story.query.filter_by(story_id=story_id).first()
        pairs=[]
        for i, pair in enumerate(story.story_sequence):
            intent_name=models.Intent.query.filter_by(
                intent_id=pair[0]
            ).first().intent_name
            
            action_name=models.Action.query.filter_by(
                action_id=pair[1]
            ).first().action_name
            
            expressions=models.Expression.query.with_entities(
                models.Expression.expression_text
            ).filter_by(intent_id=pair[0]).limit(5).all()

            response=models.Response.query.filter_by(
                intent_id=pair[0], action_id=pair[1]
            ).first()

            pairs.append({
                'index': i,
                'intent_name': intent_name,
                'action_name': action_name,
                'expressions': [e[0] for e in expressions],
                'response': response.response_text
            })
        
        return jsonify({
                'story_name': story.story_name,
                'story_sequence':pairs
            })
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)


            


@story.route('/storyEdit/<story_id>', methods=['POST'])
def storyEdit(story_id):
    try:
        data=request.get_json()
        story=models.Story.query.filter_by(
            story_id=story_id
        ).first()
        if 'story_sequence' in data:
            story_sequence=data['story_sequence']
            old_story_sequence=story.story_sequence
            deleted_pairs=set(range(0, len(old_story_sequence)))-set(story_sequence)

            for i in deleted_pairs:
                pair=old_story_sequence[i]
                db.session.query(models.StoryPair).filter_by(
                    intent_id=pair[0], action_id=pair[1], story_id=story_id
                ).delete()
                
            story.update({
                'story_sequence': [old_story_sequence[i] for i in story_sequence]
            })
         
        if 'story_name' in data:

            results = models.Story.query.filter_by(
                story_name=story_name
            ).all()

            if len(results) > 0:
                return ('Story name already exists', 400)

            story.update({
                'story_name': data['story_name']
            })

        db.session.commit()
        return utils.result('story updated', {
                'story_id': story_id
            })
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)