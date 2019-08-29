import os
import sys
# A little hack to find the project modules, no idea what is the perfect solution
sys.path.append(os.path.join(os.getcwd(), 'crudRasa'))

import json
import pandas as pd

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

from orm import utils

from dotenv import load_dotenv
load_dotenv()

import yaml

import argparse

PATH_FILE_NLU_JSON = './crudRasa/migration/static/nlu_data.json'
PATH_FILE_NLU_MD = './crudRasa/migration/static/nlu_data.md'
PATH_FILE_YAML = './crudRasa/migration/static/domain.yml'
PATH_FILE_STORIES = './crudRasa/migration/static/stories.md'
PATH_FILE_SQLSCRIPT = './crudRasa/static/dbcreate.sql'



def migrateDatabase(nluPath=PATH_FILE_NLU_MD, storiesPath=PATH_FILE_STORIES, 
    domainPath=PATH_FILE_YAML, nluJsonFormat=False, local=False):
    conn = None
    try:
        if local:
            conn = psycopg2.connect(os.environ['DATABASE_URL_STRING_LOCAL'])
        else:
            conn = psycopg2.connect(os.environ['DATABASE_URL_STRING'])
        cur = conn.cursor()
        
        print('Dropping schema of database')
        with open(os.path.abspath(PATH_FILE_SQLSCRIPT), 'r') as f:
            user = "rasaadmin"
            if local:
                user = "postgres"
            cur.execute(sql.SQL(f.read())
                .format(sql.Identifier(user)))

        print('Created new schema for database\n')
        
        
        agentSelect = "SELECT agent_id FROM rasa_ui.agents"
        cur.execute(agentSelect)
        agent_id = cur.fetchone()

        data = {}
        
        if agent_id is None:
            cur.execute("INSERT INTO rasa_ui.agents (agent_name) VALUES ('agent') \
                RETURNING agent_id")
            print('Inserting agent')
            agent_id = cur.fetchone()
            data['agentInserted'] = 1
            
        agent_id = agent_id[0]

        
        intentsData = []
        if nluJsonFormat:
            print('\nReading nlu data in JSON format')
            with open(os.path.abspath(nluPath), 'r', encoding="utf-8") as f:
                jsonData = json.loads(f.read())['rasa_nlu_data']

            
            for intent in jsonData['common_examples']:
                intentsData.append([
                    intent['intent'], 
                    intent['text'], 
                    utils.lemmatize(intent['text'])
                ])
        else:
            print('\nReading nlu data in MD format')
            with open(os.path.abspath(nluPath), 'r') as f:
                nluData = f.readlines()

            intentName = None
            for line in nluData:
                if line.strip()[:2] == '##':
                    intentName = line.strip()[10:]
                elif line.strip()[:1] == '-':
                    expression = line.strip()[2:]
                    intentsData.append([intentName, expression, utils.lemmatize(expression)])
                else:
                    continue
        
            
        intents = pd.DataFrame(
            columns=['intent_name', 'expression_text', 'lemmatized_text'],
            data = intentsData
        )

        intentToId = {}

        intentInj = "INSERT INTO rasa_ui.intents (intent_name, agent_id) VALUES (%s, %s) \
            ON CONFLICT DO NOTHING RETURNING intent_id"

        for name in intents.intent_name.unique():
            try:
                cur.execute(intentInj, (name, agent_id))
                print(f'Inserting intent {name}')
                intentToId[name]=cur.fetchone()[0]
            except Exception as e:
                print(str(e))
        actionToId = {}

        actionInj = "INSERT INTO rasa_ui.actions (action_name, agent_id) VALUES (%s, %s) \
                ON CONFLICT DO NOTHING RETURNING action_id"

        for name in intents.intent_name.unique():
            try:
                cur.execute(actionInj, ('utter_'+name, agent_id))
                print(f'Inserting action {name}')
                actionToId['utter_'+name]=cur.fetchone()[0]
            except Exception as e:
                print(str(e))

        expressionInj = "INSERT INTO rasa_ui.expressions (intent_id, expression_text, lemmatized_text) \
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
            
        for _, row in intents.iterrows():
            try:
                cur.execute(
                    expressionInj, 
                    (intentToId[row['intent_name']], row['expression_text'], row['lemmatized_text'])
                )
                print(f'Inserting expression for intent {row["intent_name"]}')
            except Exception as e:
                print(str(e))
        
        print('\nReading domain data')
        with open(os.path.abspath(PATH_FILE_YAML), 'r', encoding="utf-8") as f:
            ymlFile = yaml.safe_load(f)

        for intent in ymlFile['intents']:
            if intent not in intentToId:
                try:
                    cur.execute(intentInj, (intent, agent_id))
                    print(f'Inserting intent that is not in intents but in actions {intent}')
                    intentToId[intent]=cur.fetchone()[0]
                except Exception as e:
                    print(str(e))
        
        actionInj = "INSERT INTO rasa_ui.actions (action_name, agent_id) VALUES (%s, %s) \
                ON CONFLICT DO NOTHING RETURNING action_id"
        
        for action in ymlFile['templates']:
            if action not in actionToId:
                try:
                    cur.execute(actionInj, (action, agent_id))
                    print(f'Inserting action without intent {action}')
                    actionToId[action]=cur.fetchone()[0]
                except Exception as e:
                    print(str(e))

        responseInj = "INSERT INTO rasa_ui.responses (intent_id, action_id, buttons_info, response_text, \
            response_type) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        
        for response in ymlFile['templates']:
            intentId = intentToId[response[6:]]
            actionId = actionToId[response]
            for responseDetails in ymlFile['templates'][response]:
                text = responseDetails['text']

                buttons = None
                if 'buttons' in responseDetails:
                    buttons = []
                    for i, button in enumerate(responseDetails['buttons']):
                        buttons.append({
                            'seq': i,
                            'title': button['title'],
                            'payload': button['payload']
                        })
                try:
                    cur.execute(responseInj, (
                        str(intentId), 
                        str(actionId),
                        Json(buttons) if buttons is not None else None,
                        text, 
                        str(1)
                    ))
                    print(f'Inserting response for intent {response[6:]}')
                except Exception as e:
                    print(str(e))
        
        print('\nReading stories data')
        with open(os.path.abspath(storiesPath), 'r') as f:
            storiesData = f.readlines()

        stories = []
        story = []
        for line in storiesData:
            if line.strip()[:2] == '##':
                if len(story) == 0:
                    continue
                stories.append(story)
                story = []
            elif line.strip()[:1] == '*':
                intent_name = line.strip()[2:]
                story.append(intent_name)
            else:
                continue
        
        intentStoryInj = "INSERT INTO rasa_ui.intent_story (parent_id, intent_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"

        for story in stories:
            if len(story) == 0:
                continue
            print(f'Inserting intent story for intent {story[-1]}')
            for i in range(1, len(story)):
                parentId = intentToId[story[i-1]]
                intentId = intentToId[story[i]]
                try:
                    cur.execute(intentStoryInj, (
                        parentId, 
                        intentId,
                    ))
                except Exception as e:
                    print(str(e))

        conn.commit()
        print('\nMigration completed')
            
    except Exception as e:
        print(str(e))
    finally:
        if conn is not None:
            conn.close()
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Refresh the database schema and migrate database')
    parser.add_argument('--json', action='store_true', help='set if NLU file is in JSON format (default md format)')
    parser.add_argument('--nlu', default=None, help='path to NLU file')
    parser.add_argument('--stories', default=PATH_FILE_STORIES, help='path to stories.md file')
    parser.add_argument('--domain', default=PATH_FILE_YAML, help='path to domain.yml file')
    parser.add_argument('--local', action='store_true', help='set if migrating locally (default remote)')
    args = parser.parse_args()
    if args.json and args.nlu is None:
        args.nlu = PATH_FILE_NLU_JSON
    elif not args.json and args.nlu is None:
        args.nlu = PATH_FILE_NLU_MD
    migrateDatabase(nluPath=args.nlu, storiesPath=args.stories, domainPath=args.domain, nluJsonFormat=args.json, local=args.local)