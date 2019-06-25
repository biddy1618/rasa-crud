# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app import db


t_active_user_count_12_months = Table(
    'active_user_count_12_months', db.metadata,
    Column('count_users', BigInteger),
    Column('month_year', Text)
)


t_active_user_count_30_days = Table(
    'active_user_count_30_days', db.metadata,
    Column('user_count', BigInteger),
    Column('month_date', Text)
)


class Agent(db.Model):
    __tablename__ = 'agents'

    agent_id = Column(Integer, primary_key=True, server_default=text("nextval('agents_agent_id_seq'::regclass)"))
    agent_name = Column(String)
    endpoint_enabled = Column(Boolean, server_default=text("false"))
    rasa_core_enabled = Column(Boolean, server_default=text("false"))
    endpoint_url = Column(String)
    basic_auth_username = Column(String)
    basic_auth_password = Column(String)
    client_secret_key = Column(Text, nullable=False, server_default=text("md5((random())::text)"))
    story_details = Column(Text)
    rasa_nlu_pipeline = Column(String, server_default=text("'spacy_sklearn'::character varying"))
    rasa_nlu_language = Column(String, server_default=text("'en'::character varying"))
    rasa_nlu_fixed_model_name = Column(String)

    def serialize(self):
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'endpoint_enabled': self.endpoint_enabled,
            'rasa_core_enabled': self.rasa_core_enabled,
            'endpoint_url': self.endpoint_url,
            'basic_auth_username': self.basic_auth_username,
            'basic_auth_password': self.basic_auth_password,
            'client_secret_key': self.client_secret_key,
            'story_details': self.story_details,
            'rasa_nlu_pipeline': self.rasa_nlu_pipeline,
            'rasa_nlu_language': self.rasa_nlu_language,
            'rasa_nlu_fixed_model_name': self.rasa_nlu_fixed_model_name
        }


t_avg_nlu_response_times_30_days = Table(
    'avg_nlu_response_times_30_days', db.metadata,
    Column('round', Numeric),
    Column('month_date', Text)
)


t_avg_user_response_times_30_days = Table(
    'avg_user_response_times_30_days', db.metadata,
    Column('round', Numeric),
    Column('month_date', Text)
)


t_entities_parameters = Table(
    'entities_parameters', db.metadata,
    Column('agent_id', Integer),
    Column('agent_name', String),
    Column('messages_id', Integer),
    Column('timestamp', DateTime),
    Column('user_id', String),
    Column('user_name', String),
    Column('message_text', String),
    Column('user_message_ind', Boolean),
    Column('entity_id', Integer),
    Column('entity_name', String),
    Column('slot_data_type', String),
    Column('entity_start', Integer),
    Column('entity_end', Integer),
    Column('parameter_value', String),
    Column('parameter_id', Integer)
)


t_expression_parameters = Table(
    'expression_parameters', db.metadata,
    Column('expression_id', Integer),
    Column('parameter_required', Boolean),
    Column('parameter_value', String),
    Column('parameter_start', Integer),
    Column('parameter_end', Integer),
    Column('entity_id', Integer),
    Column('parameter_id', Integer),
    Column('intent_id', Integer),
    Column('entity_name', String)
)


t_intent_usage_by_day = Table(
    'intent_usage_by_day', db.metadata,
    Column('count', BigInteger),
    Column('to_char', Text)
)


t_intent_usage_total = Table(
    'intent_usage_total', db.metadata,
    Column('count', BigInteger)
)


t_intents_most_used = Table(
    'intents_most_used', db.metadata,
    Column('intent_name', String),
    Column('agent_id', Integer),
    Column('agent_name', String),
    Column('grp_intent_count', BigInteger)
)


t_messages_expressions = Table(
    'messages_expressions', db.metadata,
    Column('agent_id', Integer),
    Column('agent_name', String),
    Column('messages_id', Integer),
    Column('timestamp', DateTime),
    Column('user_id', String),
    Column('user_name', String),
    Column('message_text', String),
    Column('message_rich', JSONB(astext_type=Text())),
    Column('user_message_ind', Boolean),
    Column('intent_id', Integer),
    Column('intent_name', String),
    Column('expression_id', Integer)
)


class NluLog(db.Model):
    __tablename__ = 'nlu_log'

    log_id = Column(Integer, primary_key=True, server_default=text("nextval('nlu_log_log_id_seq'::regclass)"))
    timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    ip_address = Column(String)
    query = Column(String)
    event_data = Column(String)
    event_type = Column(String)


t_request_usage_total = Table(
    'request_usage_total', db.metadata,
    Column('count', BigInteger)
)


class ResponseType(db.Model):
    __tablename__ = 'response_type'

    response_type_id = Column(Integer, primary_key=True, server_default=text("nextval('response_type_response_type_id_seq'::regclass)"))
    response_type_text = Column(String)


t_settings = Table(
    'settings', db.metadata,
    Column('setting_name', String),
    Column('setting_value', String)
)


t_unique_intent_entities = Table(
    'unique_intent_entities', db.metadata,
    Column('intent_id', Integer),
    Column('entity_name', String)
)


class Action(db.Model):
    __tablename__ = 'actions'

    action_name = Column(String, nullable=False)
    agent_id = Column(ForeignKey('agents.agent_id', ondelete='CASCADE'))
    action_id = Column(Integer, primary_key=True, server_default=text("nextval('actions_action_id_seq'::regclass)"))

    agent = relationship('Agent')


class Entity(db.Model):
    __tablename__ = 'entities'

    entity_id = Column(Integer, primary_key=True, server_default=text("nextval('entities_entity_id_seq'::regclass)"))
    entity_name = Column(String)
    agent_id = Column(ForeignKey('agents.agent_id', ondelete='CASCADE'), nullable=False)
    slot_data_type = Column(String, nullable=False, server_default=text("'NOT_USED'::character varying"))

    agent = relationship('Agent')


class Intent(db.Model):
    __tablename__ = 'intents'

    intent_name = Column(String, nullable=False)
    agent_id = Column(ForeignKey('agents.agent_id', ondelete='CASCADE'))
    endpoint_enabled = Column(Boolean)
    intent_id = Column(Integer, primary_key=True, server_default=text("nextval('intents_intent_id_seq'::regclass)"))

    agent = relationship('Agent')


class Regex(db.Model):
    __tablename__ = 'regex'

    regex_id = Column(Integer, primary_key=True, server_default=text("nextval('regex_id_seq'::regclass)"))
    regex_name = Column(String)
    regex_pattern = Column(String)
    agent_id = Column(ForeignKey('agents.agent_id', ondelete='CASCADE'), nullable=False)

    agent = relationship('Agent')


class Synonym(db.Model):
    __tablename__ = 'synonyms'

    synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('synonyms_synonym_id_seq'::regclass)"))
    agent_id = Column(ForeignKey('agents.agent_id', ondelete='CASCADE'), nullable=False)
    synonym_reference = Column(String, nullable=False)

    agent = relationship('Agent')


class Expression(db.Model):
    __tablename__ = 'expressions'

    intent_id = Column(ForeignKey('intents.intent_id', ondelete='CASCADE'), nullable=False)
    expression_text = Column(String, nullable=False)
    expression_lemmatized = Column(String, nullable=False)
    expression_id = Column(Integer, primary_key=True, server_default=text("nextval('expressions_expression_id_seq'::regclass)"))

    intent = relationship('Intent')


class Message(db.Model):
    __tablename__ = 'messages'

    messages_id = Column(Integer, primary_key=True, server_default=text("nextval('messages_messages_id_seq'::regclass)"))
    timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    agent_id = Column(ForeignKey('agents.agent_id', ondelete='CASCADE'))
    user_id = Column(String)
    user_name = Column(String)
    message_text = Column(String)
    message_rich = Column(JSONB(astext_type=Text()))
    user_message_ind = Column(Boolean)
    intent_id = Column(ForeignKey('intents.intent_id', ondelete='SET NULL'))

    agent = relationship('Agent')
    intent = relationship('Intent')


class Response(db.Model):
    __tablename__ = 'responses'

    response_id = Column(Integer, primary_key=True, server_default=text("nextval('responses_response_id_seq'::regclass)"))
    intent_id = Column(ForeignKey('intents.intent_id', ondelete='CASCADE'))
    action_id = Column(ForeignKey('actions.action_id', ondelete='CASCADE'))
    buttons_info = Column(JSONB(astext_type=Text()))
    response_image_url = Column(String)
    response_text = Column(String)
    response_type = Column(ForeignKey('response_type.response_type_id', ondelete='CASCADE'))

    action = relationship('Action')
    intent = relationship('Intent')
    response_type1 = relationship('ResponseType')


class SynonymVariant(db.Model):
    __tablename__ = 'synonym_variant'

    synonym_variant_id = Column(Integer, primary_key=True, server_default=text("nextval('synonym_variant_synonym_id_seq'::regclass)"))
    synonym_value = Column(String)
    synonym_id = Column(ForeignKey('synonyms.synonym_id', ondelete='CASCADE'))

    synonym = relationship('Synonym')


class CoreParseLog(db.Model):
    __tablename__ = 'core_parse_log'

    core_parse_log_id = Column(Integer, primary_key=True, server_default=text("nextval('core_parse_log_core_parse_log_id_seq'::regclass)"))
    messages_id = Column(ForeignKey('messages.messages_id', ondelete='CASCADE', match='FULL'), nullable=False)
    timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    action_name = Column(String)
    slots_data = Column(JSONB(astext_type=Text()))
    user_response_time_ms = Column(Integer)
    core_response_time_ms = Column(Integer)

    messages = relationship('Message')


class MessagesEntity(db.Model):
    __tablename__ = 'messages_entities'

    message_id = Column(ForeignKey('messages.messages_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    entity_id = Column(ForeignKey('entities.entity_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    entity_start = Column(Integer, primary_key=True, nullable=False)
    entity_end = Column(Integer, primary_key=True, nullable=False)
    entity_value = Column(String)
    entity_confidence = Column(Integer, nullable=False)

    entity = relationship('Entity')
    message = relationship('Message')


class NluParseLog(db.Model):
    __tablename__ = 'nlu_parse_log'

    parse_log_id = Column(Integer, primary_key=True, server_default=text("nextval('parse_log_parse_log_id_seq'::regclass)"))
    messages_id = Column(ForeignKey('messages.messages_id', ondelete='CASCADE', match='FULL'), nullable=False)
    timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    intent_name = Column(String)
    entity_data = Column(JSONB(astext_type=Text()))
    intent_confidence_pct = Column(Integer)
    user_response_time_ms = Column(Integer)
    nlu_response_time_ms = Column(Integer)

    messages = relationship('Message')


class Parameter(db.Model):
    __tablename__ = 'parameters'

    parameter_required = Column(Boolean)
    parameter_value = Column(String)
    expression_id = Column(ForeignKey('expressions.expression_id', ondelete='CASCADE'), nullable=False)
    parameter_start = Column(Integer, nullable=False)
    parameter_end = Column(Integer, nullable=False)
    entity_id = Column(ForeignKey('entities.entity_id', ondelete='CASCADE'))
    parameter_id = Column(Integer, primary_key=True, server_default=text("nextval('parameters_parameter_id_seq'::regclass)"))

    entity = relationship('Entity')
    expression = relationship('Expression')
