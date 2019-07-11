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



