
## According to created configurations set “APP_SETTINGS” environment variable by running this in the terminal
`export APP_SETTINGS="config.DevelopmentConfig"`

## Also add “DATABASE_URL” to environment variables. In this case our database URL is based on the created database. So, export the environment variable by this command in the terminal,
`export DATABASE_URL="postgresql://postgres:admin@localhost:5432/rasaui"`

## Creating models for PostgreSQL database using `sqlacodegen` library
```
pip install psycopg2
pip install sqlacodegen
```
Then run following

`sqlacodegen postgresql://postgres:admin@localhost:5432/rasaui > models.py`

change the 
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

![dbRelations](./schema.png)

# Database operations

![dbOperations](./CRUDOperations.png)


