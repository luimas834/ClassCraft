# app

The FastAPI application: the app itself (`main.py`), its configuration, the database session, the
dependencies used by the endpoints, security, error handling, and the folders below.

Routers stay thin. They read the request, call a service and return a schema; the rules of the
business live in `services/`.
