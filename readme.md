## Setting up the database schema

From the postgres terminal download the schema file `dbcreate.sql` (modified file of original RasaUI database).
```
postgresTerminal:~$ wget https://raw.githubusercontent.com/biddy1618/rasaCrud/master/crudRasa/static/dbcreate.sql
```
Then create the database by running the downloaded script.


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
```
sqlacodegen postgresql://postgres:admin@localhost:5432/rasaui > models.py
mv models.py ./crudRasa/models/models.py
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

`models` folder - holds ORM models for the database. `models.Helper` class implements serialization of the ORM results into JSON format, also implements the update operation for ORM models.

---

`routes` folder - holds the implementation of endpoint routes for the CRUD operations.

---

`static` folder - holds static files.

## Notes

One can't do ORM operations with `sqlalchemy.Table`. 

One cannot use the Table objects to do proper ORM. When user queries a Table object (via `session.query(query)`) he/she will get the results returned to you as read-only namedtuple-like objects. Setting their attributes makes no sense this way makes no sense.

---

Alter the database, so that `Settings` table has a primary key. Tables need to have primary key in order to map a particular table.

> The SQLAlchemy ORM, in order to map to a particular table, needs there to be at least one column denoted as a primary key column; multiple-column, i.e. composite, primary keys are of course entirely feasible as well. These columns do not need to be actually known to the database as primary key columns, though it’s a good idea that they are. It’s only necessary that the columns behave as a primary key does, e.g. as a unique and not nullable identifier for a row.
>
> Most ORMs require that objects have some kind of primary key defined because the object in memory must correspond to a uniquely identifiable row in the database table; at the very least, this allows the object can be targeted for `UPDATE` and `DELETE` statements which will affect only that object’s row and no other. However, the importance of the primary key goes far beyond that. In SQLAlchemy, all ORM-mapped objects are at all times linked uniquely within a `Session` to their specific database row using a pattern called the identity map, a pattern that’s central to the unit of work system employed by SQLAlchemy, and is also key to the most common (and not-so-common) patterns of ORM usage.
> 
> Note:
> > It’s important to note that we’re only talking about the SQLAlchemy ORM; an application which builds on Core and deals only with `Table` objects, `select()` constructs and the like, does not need any primary key to be present on or associated with a table in any way (though again, in SQL, all tables should really have some kind of primary key, lest you need to actually update or delete specific rows).

---

__TESTING POSTGRES__:

To allow remote connections to PostgreSQL server, change the line in file _/etc/postgresql/9.5/main/postgresql.conf_:

`listen_addresses = 'localhost'` to `listen_addresses = '*'`

and add entry in file _/etc/postgresql/9.5/main/pg\_hba.conf_:
```
# TYPE  DATABASE        USER    CIDR-ADDRESS    METHOD
local   all     all     md5
host    all     all     0.0.0.0/0       md5
```
## TODO

Read about the query types: `models.Entity.query` and `db.session.query(models.Entity)`. The advantage of the later one is that if ORM table `models.Entity` has column `query`, then `models.Entity.query` will return `sqlalchemy.orm.attributes.InstrumentedAttribute` where as `db.session.query(models.Entity)` will return actual Query object `flask_sqlalchemy.BaseQuery`. Thus, if entity has column `query` then it is better to use the latter one. 

Example: `routes/log.py` where `NluLogs` entity has column named `query`.