import psycopg2
import ruamel.yaml
import json
import os

PATH_FILE = "./crudRasa/migration/static/domain.yml"

yaml = ruamel.yaml.YAML()

intent_id = 1000000000
agent_id = 1


with open(os.path.abspath(PATH_FILE), 'r', encoding="utf-8") as fp:
    data = yaml.load(fp)
    actions = data['actions']
    for i in actions:
        connection = psycopg2.connect(user="postgres",
                                      password="admin",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="rasaui")
        cursor_name = connection.cursor()
        cursor_text = connection.cursor()
        postgres_insert_action_name = """ INSERT INTO rasa_ui.actions (action_name, agent_id, action_id) VALUES (%s,%s,%s);"""

        postgres_insert_action_text = """ INSERT INTO rasa_ui.responses (action_id, buttons_info, response_text, response_id) VALUES (%s,%s,%s,%s);"""

        response = data['templates'][i]

        for k in response:
            text = k['text']
            try:
                button = k['buttons']
            except:
                button = None

            if button == None:
                record_to_insert_action_name = (i, agent_id, intent_id,)
                try:
                    cursor_name.execute(postgres_insert_action_name, record_to_insert_action_name)
                except:
                    connection.rollback()

                else:
                    connection.commit()
                record_to_insert_action_text = (intent_id, None, text ,intent_id,)
                try:
                    cursor_text.execute(postgres_insert_action_text, record_to_insert_action_text)
                except:
                    connection.rollback()
                else:
                    connection.commit()

            elif button != None:

                record_to_insert_action_name = (i, agent_id, intent_id)
                try:
                    cursor_name.execute(postgres_insert_action_name, record_to_insert_action_name)
                except:

                    connection.rollback()

                else:
                    connection.commit()

                my_list = list()
                seq = 0
                for j in button:
                    my_dict = dict()
                    my_dict["seq"] = seq
                    my_dict["title"] = j["title"]
                    my_dict["payload"] = j["payload"]
                    my_list.append(my_dict)
                    seq = seq + 1

                my_json = json.dumps(my_list)

                postgres_insert_action_text_bla = """ INSERT INTO rasa_ui.responses (buttons_info,action_id,response_text,response_id) VALUES (%s,%s,%s,%s) returning buttons_info;"""

                try:
                    cursor_text.execute(postgres_insert_action_text_bla, (my_json, intent_id, text, intent_id,))
                except:
                    connection.rollback()
                else:
                    connection.commit()

        intent_id = intent_id + 1


