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


def dump(local=False, jsonNlu=False):
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
            
        storySql = "SELECT parent_id, intent_id from rasa_ui.intent_story"
        cur.execute(storySql)
        results = cur.fetchall()

        child2parent = {}
        children, parents = set(), set()
        for p, c in results:
            child2parent[c] = p
            children.add(c)
            parents.add(p)
        
        singleIntents = list(intentIds - parents.union(children))
        children = children - parents

        stories = []
        for c in children:
            story = []
            story.append(c)
            while c in child2parent:
                c = child2parent[c]
                story.append(c)
            story.reverse()
            stories.append(story)

        for i, e in enumerate(singleIntents):
            singleIntents[i] = id2intents[e]
        
        for story in stories:
            for i, s in enumerate(story):
                story[i] = id2intents[s]
        
        singleIntents = sorted(singleIntents)
        stories = sorted(stories)

        with open(os.path.abspath(FILE_STORIES), 'w') as f:
            for intent in singleIntents:
                f.write(f'## story {intent}\n')
                f.write(f'* {intent}\n')
                f.write(f'  - utter_{intent}\n\n')
            
            for story in stories:
                f.write(f'\n## story {story[-1]}_story\n')
                for sIntent in story:
                    f.write(f'* {sIntent}\n')
                    f.write(f'  - utter_{sIntent}\n')        
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate train files from database')
    parser.add_argument('--local', action='store_true', help='set if reading local database (default remote)')
    parser.add_argument('--json', action='store_true', help='set if nlu data should be generated in json format')
    args = parser.parse_args()
    
    dump(local=args.local, jsonNlu=args.json)