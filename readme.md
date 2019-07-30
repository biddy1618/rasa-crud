## Setting up the database schema

From the postgres terminal download the schema file `dbcreate.sql` (modified file of original RasaUI database).
```
postgresTerminal:~$ wget https://raw.githubusercontent.com/biddy1618/rasa-crud/develop/crudRasa/static/dbcreate.sql
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
sqlacodegen postgresql://postgres:admin@localhost:5432/rasaui > tempModels.py
```

Then modify `tempModels.py` accordingly:
* Add helper class for serialization and update
* Link Flask's `db = SQLAlchemy(app)` to models and update accordingly (Base class and metadata)

# Database relations
![dbRelations](./schema.png)

# Database operations

![dbOperations](./CRUDOperations.png)

## Progress on endpoints

One can view the status of implementations of endpoints in [Google docs](https://docs.google.com/spreadsheets/d/1hGiSk72mFg_tV9DRYRJDW8FPHNSHuC-0TR2pqpIz0q0/edit?usp=sharing).

## Information regarding the project

`app.py` - sets up the Flask server along with SQLAlchemy settings.

---

`config.py` - holds the deployment settings for the Flask server. In order to change the deployment settings change the `.evn` file for corresponding setting in `config.py`.

---

`run.py` - main script to run in order the start the server.

---

`migration` folder - holds scripts for migrating data from DialogFlow to Rasa.

---

`orm` folder - holds ORM models for the database. `models.Helper` class implements serialization of the ORM results into JSON format, also implements the update operation for ORM models.

---

`routes` folder - holds the implementation of endpoint routes for the CRUD operations.

---

`static` folder - holds static files.

## Docker

Very basic tutorial on __Docker__ is [here](https://jonnylangefeld.github.io/learning/Docker/How%2Bto%2BDocker.html)


Also check out this [post](https://linuxize.com/post/how-to-remove-docker-images-containers-volumes-and-networks/) regarding removal of containers, images, docker objects, etc.

Very good reference to __Docker__ commands in this [Medium post](https://towardsdatascience.com/15-docker-commands-you-should-know-970ea5203421)

* `docker images -a` - list all images.
* `docker ps -a` - list all containers.
* `docker system prune` - remove all stopped containers, all dangling images, and all unused networks.
* `docker exec -ti CONTAINER /bin/bash` - start Unix shell in the container.
* `docker image|container rm IMAGE_ID|CONTAINER_ID` - remove image or container.
* `docker build -t name:tag .` - to build image from Dockerfile.
* `docker run -p DOCKER_HOST_PORT:CONTAINER_PORT name:tag` - run container. `-p` (`--publish`) to publish container's port to the host, `-d` (`--detach`) to run container in background.

---

One should add option `-y` to automatically asnwer `yes` to prompt while runnnig shell commands and also merge `RUN ...` commands into one, i.e. in Dockerfile
```
...
RUN apt-get update &&\
    apt-get install --yes python-dev graphviz libgraphviz-dev pkg-config &&\
    pip install -r requirements.txt
...
```


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
---
__GIT Commands__

In order to pull the last changes, but retain local changes (there may be conflicts), do the following:
```
git stash
git pull
git stash pop
```

---
## TODO

* Fix all inserts related to JSON column.
* Alter the database declaration so that tables _intents_ and _actions_ have unique _names_. Also table _reponses_ should have unique _intent\_id_, _action\_id_, _buttons\_info_, _response\_text_, and table _expressions_ should have unqiue _intent\_id_ and _epxression\_text_.

## Rasa Details

Responses
* Intent can have several responses, for instance in `domain.yml` file:
```
...
templates:
  utter_greet:
    - text: "hey there {name}!"  # {name} will be filled by slot (same name) or by custom action
  utter_channel:
    - text: "this is a default channel"
    - text: "you're talking to me on slack!"  # if you define channel-specific utterances, the bot will pick
      channel: "slack"                        # from those when talking on that specific channel
  utter_goodbye:
    - text: "goodbye 😢"   # multiple templates - bot will randomly pick one of them
    - text: "bye bye 😢"
  utter_default:   # utterance sent by action_default_fallback
    - text: "sorry, I didn't get that, can you rephrase it?"
...
```