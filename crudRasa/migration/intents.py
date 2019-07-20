import psycopg2
import json
import pickle
import os

agent_id = 1
PATH_INTENT = './crudRasa/migration/static/intent_name.pickle'
PATH_NLU_FILE = './crudRasa/migration/static/nlu_data.json'

with open(os.path.abspath(PATH_INTENT), "rb") as f:
    list_intent_name = pickle.load(f)

agent_id = 1

with open(os.path.abspath(PATH_NLU_FILE), 'r', encoding='utf-8') as fh:
    data = json.loads(fh.read())

    intent_id = 1000000000

    for i in list_intent_name:
        print(i)
        connection = psycopg2.connect(user="postgres",
                                      password="admin",
                                      host="localhost",
                                      port="5432",
                                      database="rasaui")
        cursor_name = connection.cursor()
        cursor_text = connection.cursor()
        postgres_insert_intent_name = """ INSERT INTO rasa_ui.intents (intent_name, agent_id, intent_id) VALUES (%s,%s,%s);"""

        postgres_insert_intent_text = """ INSERT INTO rasa_ui.expressions (intent_id, expression_text, lemmatized_text) VALUES (%s,%s,%s);"""

        for x in data['rasa_nlu_data']['common_examples']:

            intent_name = x['intent']

            intent_text = x['text']

            intent_lemma_text = x['lemma_text']

            if intent_name == i:

                change_status = 0

                record_to_insert_intent_name = (i, agent_id, intent_id)

                try:
                    cursor_name.execute(postgres_insert_intent_name, record_to_insert_intent_name)
                except:

                    connection.rollback()

                else:
                    connection.commit()

                record_to_insert_intent_text = (intent_id, intent_text, intent_lemma_text)
                try:
                    cursor_text.execute(postgres_insert_intent_text, record_to_insert_intent_text)
                except:
                    connection.rollback()
                else:
                    connection.commit()
            else:
                change_status = 1
        if change_status == 1:
            intent_id = intent_id + 1
        connection.close()





