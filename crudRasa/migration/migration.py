import os
import sys
# A little hack to find the project modules, no idea what is the perfect solution
sys.path.append(os.path.join(os.getcwd(), 'crudRasa'))

import json
import pandas as pd

import psycopg2
from psycopg2.extras import Json
from orm import utils

from dotenv import load_dotenv
load_dotenv()

import ruamel.yaml

yaml = ruamel.yaml.YAML()

PATH_FILE_NLU_JSON = './crudRasa/migration/static/nlu_data.json'
PATH_FILE_NLU_MD = './crudRasa/migration/static/nlu_data.md'
PATH_FILE_YAML = './crudRasa/migration/static/domain.yml'
PATH_FILE_STORIES = './crudRasa/migration/static/stories.md'
PATH_FILE_SQLSCRIPT = './crudRasa/static/dbcreate.sql'

jsonFile = None
with open(os.path.abspath(PATH_FILE_NLU_JSON), 'r', encoding="utf-8") as f:
    jsonFile = json.loads(f.read())['rasa_nlu_data']

ymlFile = None
with open(os.path.abspath(PATH_FILE_YAML), 'r', encoding="utf-8") as f:
    ymlFile = yaml.load(f)


conn = None
try:
    # conn = psycopg2.connect(os.environ['DATABASE_URL_STRING_LOCAL'])
    # cur = conn.cursor()

    # with open(os.path.abspath(PATH_FILE_SQLSCRIPT), 'r') as f:
    #     cur.execute(f.read())
    

    # with open(os.path.abspath(PATH_FILE_STORIES), 'r') as f:
    #     storiesData = f.readlines()

    # stories = []
    # story = []
    # for line in storiesData:
    #     if line.strip()[:2] == '##':
    #         if len(story) == 0:
    #             continue
    #         stories.append(story)
    #         story = []
    #     elif line.strip()[:1] == '*':
    #         intent_name = line.strip()[2:]
    #         story.append(intent_name)
    #     else:
    #         continue
    

    with open(os.path.abspath(PATH_FILE_NLU_MD), 'r') as f:
        nluData = f.readlines()

    intentsData = []
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

    print(intents)
        


    # agentSelect = "SELECT agent_id FROM rasa_ui.agents"
    # cur.execute(agentSelect)
    # agent_id = cur.fetchone()

    # data = {}
    
    # if agent_id is None:
    #     cur.execute("INSERT INTO rasa_ui.agents (agent_name) VALUES ('agent') \
    #         RETURNING agent_id")
    #     print('Agent not found, inserting agent\n')
    #     agent_id = cur.fetchone()
    #     data['agentInserted'] = 1
        
    # agent_id = agent_id[0]

    # intentsData = []

    # for intent in jsonFile['common_examples']:
    #     intentsData.append([
    #         intent['intent'], 
    #         intent['text'], 
    #         utils.lemmatize(intent['text'])
    #     ])
    
    # intents = pd.DataFrame(
    #     columns=['intent_name', 'expression_text', 'lemmatized_text'],
    #     data = intentsData
    # )

    # intentToId = {}

    # intentInj = "INSERT INTO rasa_ui.intents (intent_name, agent_id) VALUES (%s, %s) \
    #     ON CONFLICT DO NOTHING RETURNING intent_id"

    # for name in intents.intent_name.unique():
    #     try:
    #         cur.execute(intentInj, (name, agent_id))
    #         print(f'Inserting intent {name}')
    #         intentToId[name]=cur.fetchone()[0]
    #     except Exception as e:
    #         print(str(e))
    # actionToId = {}

    # actionInj = "INSERT INTO rasa_ui.actions (action_name, agent_id) VALUES (%s, %s) \
    #         ON CONFLICT DO NOTHING RETURNING action_id"

    # for name in intents.intent_name.unique():
    #     try:
    #         cur.execute(actionInj, ('utter_'+name, agent_id))
    #         print(f'Inserting action {name}')
    #         actionToId['utter_'+name]=cur.fetchone()[0]
    #     except Exception as e:
    #         print(str(e))

    # expressionInj = "INSERT INTO rasa_ui.expressions (intent_id, expression_text, lemmatized_text) \
    #     VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        
    # for _, row in intents.iterrows():
    #     try:
    #         cur.execute(
    #             expressionInj, 
    #             (intentToId[row['intent_name']], row['expression_text'], row['lemmatized_text'])
    #         )
    #         print(f'Inserting expression for intent {row["intent_name"]}')
    #     except Exception as e:
    #         print(str(e))
    
    # for intent in ymlFile['intents']:
    #     if intent not in intentToId:
    #         try:
    #             cur.execute(intentInj, (intent, agent_id))
    #             print(f'Inserting intent that is not in intents but in actions {intent}')
    #             intentToId[intent]=cur.fetchone()[0]
    #         except Exception as e:
    #             print(str(e))
    
    # actionInj = "INSERT INTO rasa_ui.actions (action_name, agent_id) VALUES (%s, %s) \
    #         ON CONFLICT DO NOTHING RETURNING action_id"
    
    # for action in ymlFile['templates']:
    #     if action not in actionToId:
    #         try:
    #             cur.execute(actionInj, (action, agent_id))
    #             print(f'Inserting action without intent {action}')
    #             actionToId[action]=cur.fetchone()[0]
    #         except Exception as e:
    #             print(str(e))

    # responseInj = "INSERT INTO rasa_ui.responses (intent_id, action_id, buttons_info, response_text, \
    #     response_type) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
    
    # for response in ymlFile['templates']:
    #     intentId = intentToId[response[6:]]
    #     actionId = actionToId[response]
    #     for responseDetails in ymlFile['templates'][response]:
    #         text = responseDetails['text']

    #         buttons = None
    #         if 'buttons' in responseDetails:
    #             buttons = []
    #             for i, button in enumerate(responseDetails['buttons']):
    #                 buttons.append({
    #                     'seq': i,
    #                     'title': button['title'],
    #                     'payload': button['payload']
    #                 })
    #         try:
    #             cur.execute(responseInj, (
    #                 str(intentId), 
    #                 str(actionId),
    #                 Json(buttons) if buttons is not None else None,
    #                 text, 
    #                 str(1)
    #             ))
    #             print(f'Inserting response for intent {response[6:]}')
    #         except Exception as e:
    #             print(str(e))
    
    # conn.commit()
    print('\nMigration completed')
        
except Exception as e:
    print(str(e))
finally:
    if conn is not None:
        conn.close()