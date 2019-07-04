# Migration

## Notes

The data in __DialogFlow__ in interconnected in complex ways, foreign keys of one data point are attached to IDs of other data point, which serve as a primary key to the database, so when inserting new data into new database of the __Rasa platform__, we have to explicitly specify the IDs of the rows. The problem is:

In PostgreSQL database primary keys are `sequence` so they are incremented automatically, but when we insert explicitly specifying the ID's of data points (primary keys of the rows), the sequence is not incremented accordingly. As an example:

>Sequence starts with 1, but ,for instance, we insert 100 _intents_ (data points) into database, so the first ID is 1 and last is 100 accordingly. We have to explicitly specify the IDs of these _intents_ since they are directly connected to other entities in database, like _expressions_ (another entity), _responses_ (yet another entity), etc. Thus we explicitly insert into databse rows with ID. When inserting with ID, the `sequence` is not updated, i.e. say we inserted those 100 intents into databse so that the last _intent_ ID is 100. When afterwards we try to insert new _intent_, its ID will start from 1, which will lead to primary key duplication error.

In order to solve this problem it was decided to insert existing data points with IDs starting from __1000000000__ (`intents.py` and `responses.py` files):
```
intent_id = 1000000000
```
Sequence has range from 1 to 9223372036854775807 (`dbcreate.sql` file):
```
CREATE SEQUENCE seq1
INCREMENT 1
START 1
MINVALUE 1
MAXVALUE 9223372036854775807
CACHE 1;
```

## Procedure on how to fill the database

Set the connection details for the PostgreSQL database in the files `responses.py` and `intents.py`. Make sure that the database is newly created. Create a agent in the RasaUI with ID equal to 1. Run the mentioned scripts.