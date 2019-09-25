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
        return(f"Internal server error: {str(e)}", 500)

@response.route('/actionresponse', methods=['POST'])
def responseAction():
    try:
        data=request.get_json()
        addingResponse = False

        if 'story_id' in data and 'new' not in data:
            
            print('Searching for action')
            pair = models.StoryPair.query\
                .filter_by(intent_id=data['intent_id'], story_id=data['story_id'])\
                .first()
            if pair is not None:
                print('Adding response')
                action_id = pair.action_id
                print(f'Found action ID: {action_id}\n')
                addingResponse = True
            else:
                action_name='utter_action'+utils.generateName()
                results = models.Action.query.filter_by(action_name=action_name).all()
                print(f'Generated action name: {action_name}')
                while len(results) > 0:
                    story_name = 'utter_action'+utils.generateName()
                    results = models.Action.query.filter_by(action_name=action_name).all()
                    print(f'Generated action name (new): {action_name}')
                
                action=models.Action(
                    action_name=action_name
                )
                db.session.add(action)
                db.session.flush()
                action_id = action.action_id
                print(f'Inserted action: {action_name}\n')
            
        else:

            action_name='utter_action'+utils.generateName()
            results = models.Action.query.filter_by(action_name=action_name).all()
            print(f'Generated action name: {action_name}')
            while len(results) > 0:
                story_name = 'utter_action'+utils.generateName()
                results = models.Action.query.filter_by(action_name=action_name).all()
                print(f'Generated action name (new): {action_name}')
            
            action=models.Action(
                action_name=action_name
            )
            db.session.add(action)
            db.session.flush()
            action_id = action.action_id
            print(f'Inserted action: {action_name}\n')
    

        assert(action_id is not None)
        
        response=models.Response(
            intent_id=data['intent_id'],
            action_id=action_id,
            response_text=data['response_text'],
            response_type=data['response_type'],
            buttons_info=None if data['buttons_info'] is None else data['buttons_info'],          
        )
        db.session.add(response)
        print(f'Inserted response to action ID: {action_id}\n')

        if addingResponse:
            db.session.commit()
            return utils.result('success', 'Inserted response')

        if 'story_id' in data and 'new' not in data:
            print(f'Inserting new pair into story ID: {data["story_id"]}')
            story_pair=models.StoryPair(
                story_id=data['story_id'],
                intent_id=data['intent_id'],
                action_id=action_id
            )
            db.session.add(story_pair)
            print('Inserted story pair')

            story = models.Story.query.filter_by(story_id=data['story_id']).first()

            story_sequence = story.story_sequence
            story_sequence.append([data['intent_id'], action_id])
            story.update({'story_sequence': story_sequence})
            print(f'Added story pair to story ID: {story.story_id}\n')
        
        elif 'story_id' in data and 'new' in data:
            print(f'Creating new story in continuiation to story {data["story_id"]}')
            storyOld = models.Story.query.filter_by(story_id=data['story_id']).first()
                
            story_name = 'story '+utils.generateName()
            results = models.Story.query.filter_by(story_name=story_name).all()
            print(f'Story name: {story_name}')
            while len(results) > 0:
                story_name = 'story story'+utils.generateName()
                results = models.Story.query.filter_by(story_name=story_name).all()
                print(f'Story name (new): {story_name}')
            
            story_sequence = storyOld.story_sequence
            story_sequence.append([data['intent_id'], action_id])
            
            storyNew = models.Story(
                story_name=story_name,
                story_sequence=story_sequence

            )
            
            db.session.add(storyNew)
            db.session.flush()
            print(f'New ID: {storyNew.story_id}')
            print('Inserted new story')
            
            story_pair=models.StoryPair(
                story_id=storyNew.story_id,
                intent_id=data['intent_id'],
                action_id=action_id
            )
            db.session.add(story_pair)
            print('Inserted new story pair')

        else:
            print('Create new story')
            story_name = 'story story'+utils.generateName()
            results = models.Story.query.filter_by(story_name=story_name).all()
            print(f'Story name: {story_name}')
            while len(results) > 0:
                story_name = 'story story'+utils.generateName()
                results = models.Story.query.filter_by(story_name=story_name).all()
                print(f'Story name: {story_name}')

            story=models.Story(
                story_name=story_name,
                story_sequence=[[data['intent_id'], action_id]]
            )
            db.session.add(story)
            db.session.flush()
            print('Inserted new story')

            assert(story.story_id is not None)

            story_pair=models.StoryPair(
                story_id=story.story_id,
                intent_id=data['intent_id'],
                action_id=action_id
            )
            db.session.add(story_pair)
            print('Inserted new story pair')
        
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(f"Internal server error: {str(e)}", 500)

@response.route('/response/<intent_id>', methods=['GET'])
def responseIntentID(intent_id):
    try:
        storyPairs=models.StoryPair.query.filter_by(intent_id=intent_id).all()
        
        results=[]
        for triplet in storyPairs:
            story_name=models.Story.query.filter_by(
                story_id=triplet.story_id).first().story_name
            responses=models.Response.query.filter_by(
                intent_id=intent_id, action_id=triplet.action_id
            ).all()
            responses=[r.serialize() for r in responses]
            results.append({
                'story_id': triplet.story_id, 
                'story_name': story_name,
                'responses': responses
            })
        
        return jsonify({'stories': results})
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)

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
        return(f"Internal server error: {str(e)}", 500)

@response.route('/response/<response_id>', methods=['DELETE'])
def responseIntentRemove(response_id):
    try:
        temp=models.Response.query.filter_by(
            response_id=response_id
        ).first()

        results=db.session.query(models.Response.response_id)\
            .filter_by(action_id=temp.action_id).distinct().all()
        print(results)
            
        if len(results) == 1:
            
            temp2 = models.StoryPair.query.filter_by(
                action_id=temp.action_id
            ).all()

            for triplet in temp2:
                story = models.Story.query.filter_by(
                    story_id=triplet.story_id
                ).first()

                if len(story.story_sequence) == 1:
                    db.session.query(models.Story)\
                        .filter_by(story_id=story.story_id).delete()
                else:
                    seq = story.story_sequence
                    new_seq = []
                    for pair in seq:
                        if pair[0]==triplet.intent_id and \
                            pair[1]==triplet.action_id:
                            continue
                        new_seq.append(pair)
                    story.update({'story_sequence': new_seq})
                
            db.session.query(models.StoryPair)\
                .filter_by(action_id=temp.action_id).delete()
        db.session.query(models.Response)\
            .filter_by(response_id=response_id).delete()
        db.session.commit()
        return utils.result('success', f'Removed response {response_id}')
    except Exception as e:
        db.session.rollback()
        return(f"Internal server error: {str(e)}", 500)

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
        return(f"Internal server error: {str(e)}", 500)

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
        return(f"Internal server error: {str(e)}", 500)


