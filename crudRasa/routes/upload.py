from flask import request, jsonify, Blueprint

import psycopg2
from psycopg2.extras import Json

import json
import pandas as pd
from io import StringIO

from app import db
from orm import models, utils


fileUpload=Blueprint('fileUpload', __name__)

@fileUpload.route('/uploadFromFile', methods=['POST'])
def uploadFromFile():
    conn = None
    try:
        df = pd.read_csv(StringIO(request.get_json()['data']))
        
        dbData = {
            "user": 'rasaadmin',
            "password": 'Ba89elEe2j46',
            "host": 'dev-postgresql-v965.cpwuac0qgnrf.eu-west-1.rds.amazonaws.com',
            "port": '5432',
            "database": 'rasabot',
        }

        dbDataLocal = {
            "user": 'postgres',
            "password": 'admin',
            "host": 'localhost',
            "port": '5432',
            "database": 'rasaui',
        }
        
        conn = psycopg2.connect(user=dbDataLocal["user"],
                                password=dbDataLocal["password"],
                                host=dbDataLocal["host"],
                                port=dbDataLocal["port"],
                                database=dbDataLocal["database"])
        cur = conn.cursor()

        data = {}

        agentSelect = "SELECT agent_id FROM rasa_ui.agents"
        cur.execute(agentSelect)
        agent_id = cur.fetchone()
        
        if agent_id is None:
            cur.execute("INSERT INTO rasa_ui.agents (agent_name) VALUES ('agent') \
                RETURNING agent_id")
            agent_id = cur.fetchone()
            data['agentInserted'] = 1
            
        agent_id = agent_id[0]

        
        intentSelect = "SELECT intent_id, intent_name FROM rasa_ui.intents"
        
        cur.execute(intentSelect)
        results = cur.fetchall()
        intentToId = {}

        for intentId, intentName in results:
            intentToId[intentName]=intentId
        
        intents = pd.DataFrame(
            columns=['name', 'agent_id'],
            data=[[name, agent_id] for name in df.intent.unique()]
        )
        
        data['intentsNotInserted'] = list(intents[intents.name.isin(intentToId.keys())]\
            .name.values)
        
        intents = intents[~intents.name.isin(intentToId.keys())]
        data['intentsInserted'] = list(intents.name.values)
        
        intentInj = "INSERT INTO rasa_ui.intents (intent_name, agent_id) VALUES (%s, %s) \
            RETURNING intent_id"

        for _, row in intents.iterrows():
            cur.execute(intentInj, (row['name'], row['agent_id']))
            intentToId[row['name']]=cur.fetchone()[0]
        
        
        expressionSelect = "SELECT intent_id, expression_text FROM rasa_ui.expressions"

        cur.execute(expressionSelect)
        results = cur.fetchall()
        expressionsExist = [str(e[0])+'-'+e[1] for e in results]
        
        expressions = []
        for _, row in df.iterrows():
            expressions.append([
                intentToId[row['intent']], 
                row['trigger'], 
                utils.lemmatize(row['trigger'])
            ])

        expressions = pd.DataFrame(
            columns=['intent_id', 'expression_text', 'lemmatized_text'],
            data=expressions
        )
        
        data['expressionsNotInserted'] = list(expressions[(expressions.intent_id.astype(str)+'-'+\
            expressions.expression_text).isin(expressionsExist)].expression_text.values)
        
        expressions = expressions[~(expressions.intent_id.astype(str)+'-'+\
            expressions.expression_text).isin(expressionsExist)]
        data['expressionsInserted'] = list(expressions.expression_text.values)

        expressionInj = "INSERT INTO rasa_ui.expressions (intent_id, expression_text, lemmatized_text) \
            VALUES (%s, %s, %s)"
        for _, row in expressions.iterrows():
            cur.execute(
                expressionInj, 
                (row['intent_id'], row['expression_text'], row['lemmatized_text'])
            )
        
        
        actionSelect = "SELECT action_id, action_name FROM rasa_ui.actions"

        cur.execute(actionSelect)
        results = cur.fetchall()
        actionToId = {}
        for actionId, actionName in results:
            actionToId[actionName] = actionId

        actions = pd.DataFrame(
            columns=['action_name', 'agent_id'], 
            data=[['utter_'+name, agent_id] for name in df.intent.unique()]
        )
        
        data['actionsNotInserted'] = list(actions[actions.action_name.isin(actionToId.keys())]\
            .action_name.values)

        actions = actions[~actions.action_name.isin(actionToId.keys())]
        data['actionsInserted'] = list(actions.action_name.values)

        actionInj = "INSERT INTO rasa_ui.actions (action_name, agent_id) VALUES (%s, %s) \
            RETURNING action_id"

        
        for _, row in actions.iterrows():
            cur.execute(actionInj, (row['action_name'], row['agent_id']))
            actionToId[row['action_name']]=cur.fetchone()[0]

        responseSelect = "SELECT intent_id, action_id, buttons_info, response_text FROM \
            rasa_ui.responses"

        cur.execute(responseSelect)
        results = cur.fetchall()
        responseExist = [str(e[0])+'-'+str(e[1])+'-'+str(e[2])+'-'+str(e[3]) for e in results]
        responses = []
        
        for _, row in df[df.response.notna() | df.button.notna()].iterrows():
            intentId = intentToId[row['intent']]
            actionId = actionToId['utter_'+row['intent']]
            button = Json(json.loads(row['button'])) if not pd.isnull(row['button']) else None
            responseText = row['response']
            responses.append([intentId, actionId, button, responseText, 1])
        
        responses = pd.DataFrame(
            columns=['intent_id', 'action_id', 'buttons_info', 'response_text', 'response_type'],
            data=responses
        )
        
        temp = responses.intent_id.astype(str)+'-'+responses.action_id.astype(str)+'-'+\
            responses.buttons_info.astype(str)+'-'+responses.response_text.astype(str)
        data['responsesNotInserted'] = list(responses[temp.isin(responseExist)].response_text.values)

        responses = responses[~temp.isin(responseExist)]
        data['responsesInserted'] = list(responses.response_text.values)
        
        responseInj = "INSERT INTO rasa_ui.responses (intent_id, action_id, buttons_info, response_text, \
            response_type) VALUES (%s, %s, %s, %s, %s)"

        for _, row in responses.iterrows():
            cur.execute(
                responseInj, (
                    row['intent_id'], 
                    row['action_id'], 
                    row['buttons_info'], 
                    row['response_text'], 
                    row['response_type']
                )
            )
        
        
        totalInsertions = 0
        for key in data:
            if isinstance(data[key], list) and 'Not' not in key:
                totalInsertions += len(data[key])
            elif key == 'agentInserted':
                totalInsertions += data[key]
        
        data['totalInsertions'] = totalInsertions

        conn.commit()

        return (jsonify(data), 200)
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()
        