
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

`static` folder - holds static files.

## Notes

One can't do ORM operations with `sqlalchemy.Table`. 

One cannot use the Table objects to do proper ORM. When user queries a Table object (via `session.query(query)`) he/she will get the results returned to you as read-only namedtuple-like objects. Setting their attributes makes no sense this way makes no sense.

## TODO

Alter the database, so that `Settings` table has a primary key. Tables need to have primary key in order to map a particular table.

> The SQLAlchemy ORM, in order to map to a particular table, needs there to be at least one column denoted as a primary key column; multiple-column, i.e. composite, primary keys are of course entirely feasible as well. These columns do not need to be actually known to the database as primary key columns, though it’s a good idea that they are. It’s only necessary that the columns behave as a primary key does, e.g. as a unique and not nullable identifier for a row.
>
> Most ORMs require that objects have some kind of primary key defined because the object in memory must correspond to a uniquely identifiable row in the database table; at the very least, this allows the object can be targeted for `UPDATE` and `DELETE` statements which will affect only that object’s row and no other. However, the importance of the primary key goes far beyond that. In SQLAlchemy, all ORM-mapped objects are at all times linked uniquely within a `Session` to their specific database row using a pattern called the identity map, a pattern that’s central to the unit of work system employed by SQLAlchemy, and is also key to the most common (and not-so-common) patterns of ORM usage.
> 
> Note:
> > It’s important to note that we’re only talking about the SQLAlchemy ORM; an application which builds on Core and deals only with `Table` objects, `select()` constructs and the like, does not need any primary key to be present on or associated with a table in any way (though again, in SQL, all tables should really have some kind of primary key, lest you need to actually update or delete specific rows).


