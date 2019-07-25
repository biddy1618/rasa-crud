# DB operations for Rasa platform

The list of routes that are directly implemented as is:
* `actions.py`
* `agent.py`
* `entity.py`
* `expression.py`
* `intent.py`
* `log.py`
* `parameter.py`
* `regex.py`
* `response.py`
* `setting.py`
* `synonym.py`
* `variant.py`

The list of routes that are implemeted only for DB operations:
* `nlu_router.py`
* `middleware.py`
* `rasa_events.py`
* `messages.py`
* `auth.py`

## Notes

### `/messages/operation11` from `messages.py` route
This endpoint implemented using direct SQL injection since `sqlalchemy` ORM doesn't directly implement `FULL JOIN`:
>First of all, `sqlalchemy` does not support `FULL JOIN` out of the box, and for some good reasons. So any solution proposed will consist of two parts:
>* A work-around for missing functionality.
>* sqlalchemy syntax to build a query for that work-around.
>
>Other options might be as follow:
>* simply execute those two queries separately and aggregate the results already in Python itself (for not so large results sets).
>* __given that it looks like some kind of reporting functionality rather than business model workflow, create a SQL query and execute it directly via engine. (only if it really is much better performing though).__

### Upload from file - gettings `ID`s of inserted row

>You'll be better off looping over a single insert within a transaction, or using a multi-valued insert... returning, though in the latter case you must be careful to match returned IDs using another input value, you can't just assume the order of returned IDs is the same as the input VALUES list.

Thus while inserting, make sure to insert one by one.

### Inserting JSON data into PostreSQL database

You can use `psycopg2.extras.Json` to convert `dict` to `JSON` that Postgre accept.

```
from psycopg2.extras import Json

jsonData = [
    {
        "key1":{
            "key2":"value1"
        },
        "key2":[
            {
                "key1":1,
                "key2":"value2"
            },
            {
                "key1":"value1"
            }
        ]
    }
]

jsonDate=Json(jsonDate)
```



