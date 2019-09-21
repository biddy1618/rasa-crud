
# The ORM models for PostgreSQL database 

ORM was created using `sqlacodegen` library.

```
pip install psycopg2
pip install sqlacodegen
```
Then following cript should be executed to form ORM models in Python language
```
sqlacodegen postgresql://postgres:admin@localhost:5432/rasaui > orm/tempModels.py
```

Then modify `tempModels.py` accordingly:
* Add imports and helper class for serialization and update
```
from app import db
from decimal import Decimal as D

class Helper(object):

    def serialize(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data):
        for k, v in data.items():
            setattr(self, k, v)
    
    @staticmethod
    def serializeStatic(row):
        return {c: Helper.checkDecimal(getattr(row, c)) 
                for c in row.keys()}
    
    @staticmethod
    def checkDecimal(val):
        return str(val) if isinstance(val, D) else val
```
* Link Flask's `db = SQLAlchemy(app)` to models and update accordingly (Base class and metadata), i.e. replace `Base` and `metadata` with `db.Model, Helper` and `db.metadata` correspondingly

# Database relations
![dbRelations](./schema.png)

# Database operations
![dbOperations](./CRUDOperations.png)

## Modifications to database
### Additional column in `rasa_ui.expressions` table

Additional column that will hold lemmatized text of the original text:
```
lemmatized_text character varying COLLATE pg_catalog."default" NOT NULL
```

### Additional table `rasa_ui.analytics`

Additional table that will hold conversations information.
```
CREATE TABLE analytics
(
  sender_id  VARCHAR (100)  NOT NULL,
  intent_name VARCHAR (100) NOT NULL,
  response_time float NOT NULL,
  dateandtime timestamp NOT NULL DEFAULT NOW(),
  user_message  VARCHAR (600),
  bot_message  VARCHAR (600),
  session_id VARCHAR (600)
)
WITH (
  OIDS = FALSE
)
TABLESPACE pg_default;
```

### Table that corresponds to stories - `rasa_ui.stoires`

3 columns:
* `story_id` - integer primary key (for indexing)
* `story_name` - story name
* `story_sequence` - array (sequence in order) of `intent_id`, `action_id` pairs

The assumption is that there is story ID, intent ID, and action ID are always unique, i.e. there can't be same pair of intent-action in one story.

### Helper table for storing pairs of intent-action within a story - `rasa_ui.story_pairs`

3 columns:
* `intent_id` - integer intent ID
* `action_id` - integer action ID
* `story_id` - integer story ID (foreign key for `rasa_ui.stories`)

Primary key - `intent_id`, `action_id`, and `story_id`.

Operations with stories:
* `CREATE STORY` - given parent intent ID and current intent ID, create new record in `rasa_ui.intent_story` with those IDs.
* `REMOVE STORY` - when deleting parent intent from intent edit page, remove __single__ record where `intent_id` = current intent's ID and `parent_id` = parent intent's ID.
* `REMOVE INTENT` - when deleting the intent, also delete __all__ records with `intent_id` = ID of deleted intent, and `parent_id` = ID of deleted intent from table `rasa_ui.intent_story`.




