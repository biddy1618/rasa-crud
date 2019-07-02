
## Environment variables for the Flask application and database connection are set with `python-dotenv` package.

`.env` file holds environment variables to be exported. These are loaded when app starts through script in `app.py` file.
```
from dotenv import load_dotenv
load_dotenv()
```

## The ORM models for PostgreSQL database were created using `sqlacodegen` library

```
pip install psycopg2
pip install sqlacodegen
```
Then following cript should be executed to form ORM models in Python language

`sqlacodegen postgresql://postgres:admin@localhost:5432/rasaui > db/models.py`

One needs to change the 
```
Base = declarative_base()
metadata = Base.metadata
```
to
```
from app import db
Base = db.Model
metadata = db.metadata
```

# Database relations
variant
![dbRelations](./schema.png)

# Database operations

![dbOperations](./CRUDOperations.png)

## Information regarding the project

`app.py` - sets up the Flask server along with SQLAlchemy settings.

---

`config.py` - holds the deployment settings for the Flask server. In order to change the deployment settings change the `.evn` file for corresponding setting in `config.py`.

---

`run.py` - main script to run in order the start the server.

---

`utils.py` - scripts that are used throughout the project:
* `utils.lemmatize(text)` returns lemmatized text of the input `text`.
* `utils.result(status, message)` returns the status along with message (`status` and `message` parameters respectively) of DB operation in JSON suitable format.
* `utils.makeList(urlParams)` returns python list of strings of the parameters `urlParams`. Get URL-encoded parameters that are given in the form of the string list `...?a=i1,i2,i3...`.

---

`db` folder - holds ORM models for the database. `db.Serializer` class implements serialization of the ORM results into JSON format, also implements the update operation for ORM models.

---

`routes` folder - holds the implementation of endpoint routes for the CRUD operations.

---

`statis` folder - holds static files.

## Notes

One can't do ORM operations with `sqlalchemy.Table`. 

One cannot use the Table objects to do proper ORM. When user queries a Table object (via `session.query(query)`) he/she will get the results returned to you as read-only namedtuple-like objects. Setting their attributes makes no sense this way makes no sense.


