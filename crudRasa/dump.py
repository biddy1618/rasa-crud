import os
import sys

import psycopg2

from dotenv import load_dotenv
load_dotenv()

import argparse

import yaml
import json

FILE_DOMAIN = './crudRasa/static/generated/domain.yml'
FILE_STORIES = './crudRasa/static/generated/stories.md'
FILE_NLU_MD = './crudRasa/static/generated/nlu.md'
FILE_NLU_JSON = './crudRasa/static/generated/nlu.json'


def dump(local=False, jsonNlu=False, twoLevel=False, allStories=False):
    conn = None
    try:
        if local:
            conn = psycopg2.connect(os.environ['DATABASE_URL_STRING_LOCAL'])
        else:
            conn = psycopg2.connect(os.environ['DATABASE_URL_STRING'])
            
        cur = conn.cursor()

        intentSql = "SELECT intent_id, intent_name from rasa_ui.intents"
        cur.execute(intentSql)
        results = cur.fetchall()

        id2intents = {}
        intents = []
        intentIds = set()
        for id, name in results:
            id2intents[id] = name
            intents.append(name)
            intentIds.add(id)

        actionSql = "SELECT action_id, action_name from rasa_ui.actions"
        cur.execute(actionSql)
        results = cur.fetchall()

        id2actions = {}
        actions = []
        for id, name in results:
            id2actions[id] = name
            actions.append(name)
        
        responseSql = "SELECT action_id, response_text, buttons_info from rasa_ui.responses"
        cur.execute(responseSql)
        results = cur.fetchall()

        templates = {}
        for id, text, buttons in results:
            actionName = id2actions[id]
            if actionName not in templates:
                templates[actionName] = []
            
            if buttons is not None:
                buttons = [{'title': v['title'], 'payload': v['payload']} \
                    for v in buttons]
                templates[actionName].append({'text': text, 'buttons': buttons})
            else:
                templates[actionName].append({'text': text})
        
        domain = {
            'intents': sorted(intents),
            'actions': sorted(actions),
            'templates': templates
        }

        with open(os.path.abspath(FILE_DOMAIN), 'w') as f:
            noalias_dumper = yaml.dumper.SafeDumper
            noalias_dumper.ignore_aliases = lambda self, data: True      
            yaml.dump(domain, f, default_flow_style=False, 
                allow_unicode=True, Dumper=noalias_dumper)
        
        expressionsSql = "SELECT intent_id, lemmatized_text from rasa_ui.expressions"
        cur.execute(expressionsSql)
        results = cur.fetchall()

        expressions = {}
        for id, expression in results:
            intentName = id2intents[id]
            if intentName not in expressions:
                expressions[intentName] = []
            expressions[intentName].append(expression)

        if jsonNlu:
            nluJson = {
                'common_examples': [],
                'regex_features': [],
                'lookup_tables': [],
                'entity_synonyms': [],
            }
            for intent, expression in expressions.items():
                for e in expression:
                    nluJson['common_examples'].append({
                        'intent': intent,
                        'text': e,
                    })

            with open(FILE_NLU_JSON, 'w') as f:
                json.dump(nluJson, f, ensure_ascii=False)
        else:
            with open(os.path.abspath(FILE_NLU_MD), 'w') as f:
                for intent, expression in expressions.items():
                    f.write(f'## intent:{intent}\n')
                    for e in expression:
                        f.write(f'  - {e}\n')
                    f.write('\n')
            
        storySql = "SELECT story_name, story_sequence from rasa_ui.stories"
        cur.execute(storySql)
        results = cur.fetchall()

        singleStories = set()
        for story, stories in results:
            for pair in stories:
                singleStories.add(tuple(pair))

        with open(os.path.abspath(FILE_STORIES), 'w') as f:
            if allStories:
                for pair in singleStories:
                    f.write(f'## story {pair[0]}-{pair[1]}\n')
                    f.write(f'* {id2intents[pair[0]]}\n')
                    f.write(f'  - {id2actions[pair[1]]}\n')
                    f.write('\n')

                if twoLevel:
                    for story, stories in results:
                        if len(stories)>1:
                            for i in range(1, len(stories)):
                                f.write(f'## {story} {i}\n')
                                f.write(f'* {id2intents[stories[i-1][0]]}\n')
                                f.write(f'  - {id2actions[stories[i-1][1]]}\n')
                                f.write(f'* {id2intents[stories[i][0]]}\n')
                                f.write(f'  - {id2actions[stories[i][1]]}\n')
                                f.write('\n')
                else:
                    for story, stories in results:
                        if len(stories)>1:
                            f.write(f'## {story}\n')
                            for pair in stories:
                                f.write(f'* {id2intents[pair[0]]}\n')
                                f.write(f'  - {id2actions[pair[1]]}\n')
                            f.write('\n')   
            else:
                if twoLevel:
                    for story, stories in results:
                        if len(stories)==1:
                            f.write(f'## {story}\n')
                            f.write(f'* {id2intents[stories[0][0]]}\n')
                            f.write(f'  - {id2actions[stories[0][1]]}\n')
                            f.write('\n')

                        for i in range(1, len(stories)):
                            f.write(f'## {story} {i}\n')
                            f.write(f'* {id2intents[stories[i-1][0]]}\n')
                            f.write(f'  - {id2actions[stories[i-1][1]]}\n')
                            f.write(f'* {id2intents[stories[i][0]]}\n')
                            f.write(f'  - {id2actions[stories[i][1]]}\n')
                            f.write('\n')

                else:
                    for story, stories in results:
                        f.write(f'## {story}\n')
                        for pair in stories:
                            f.write(f'* {id2intents[pair[0]]}\n')
                            f.write(f'  - {id2actions[pair[1]]}\n')
                        f.write('\n')
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate train files from database')
    parser.add_argument('--local', action='store_true', help='set if reading local database (default remote)')
    parser.add_argument('--json', action='store_true', help='set if nlu data should be generated in json format')
    parser.add_argument('--twoLevel', action='store_true', help='generate stories in 2 levels (default max)')
    parser.add_argument('--allStories', action='store_true', help='generate single stories for each pair of intent-action (default false)')
    args = parser.parse_args()
    
    dump(local=args.local, jsonNlu=args.json, twoLevel=args.twoLevel, allStories=args.allStories)