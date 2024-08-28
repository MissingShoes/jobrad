# chat-service

Chat service is a simple micro service that offers an API for a customer support chat to

- start chat sessions
- send messages to chat sessions
- retrieve chat sessions

## Main Dependencies

The main dependencies of the project are:

- [Poetry](https://python-poetry.org/docs/) for dependency management.
- [Quart](https://quart.palletsprojects.com/en/latest/), an async web micro framework whose API is mostly consistent
  with flask.
- [Pydantic](https://docs.pydantic.dev/latest/) for data validation and for documenting response models.
- [SQLAlchemy](https://www.sqlalchemy.org/) with its ORM functionality.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) for database migrations
- [Typed-Settings](https://typed-settings.readthedocs.io/en/latest/getting-started.html) for structured configuration
  through TOML files.
- [Pytest](https://docs.pytest.org/en/stable/) for testing.

## Project Structure

```
├── chat_service        # main folder of the service
  ├── app.py              # initialisation and configuration of the Quart app
  ├── asgi.py             # creation of an app object, necessary for running with hypercorn
  ├── config.py           # the model for parsing the app configuration TOML files
  ├── model               # module holding the data model
    ├── __init__.py         # initialisation of the database engine and sessionmaker
    └── chat.py             # data model for the chat messages
  ├── routes.py           # implementation of the routes
  ├── schema.py           # shared data types
  ├── services.py         # services for interacting with the chat sessions
  ├── test
  └── test_routes.py      # tests for the routes
  └── transport.py
├── config              # folder holding the configuration files
└── migrations
    ├── env.py          # configuration for the alembic migration tool
    └── versions        # migration scripts
```

## Setup

### Installing Dependencies

This project uses poetry. You can install all dependencies by running

```bash
poetry install
```

### Running Tests

The project contains a couple of unit tests. Once all dependencies have been installed, you can run them using pytest:

```
poetry run pytest
```

### Formatting, Typing and Linting

This project is formatted using `black` and `isort`. It is linted using `flake8` and type checked using `mypy`.

## Running the service locally using docker-compose

In the project, there is a dockerfile and a docker-compose file provided. You can use it to run the service locally:

```bash
docker-compose up --force-recreate --build
```

You can check success by going to `localhost:8080/health`.

## Swagger Docs

Once the service is up and running, you should be able to access the Swagger docs for the API under
`localhost:8080/docs`.

# Limitations

The project is a very simple implementation of a backend service to support chat functionality. To name a few:

- The API is currently unprotected and thus not suitable for public access. Any actor could try to create chat sessions.
- The API does not know anything about user management. It only distinguishes the types of authors for each message. But
  there is no role management that would prevent malicious actors to disguise as customer service agents.
- The test suite includes only rough end-to-end tests for different flows and should be refactored to test more and more
  specific scenarios.
- The data model is very simple and is made up of a single `chat_messages` table with a minimal set of columns. A
  real-world use case would probably require additional tables such as a dedicated `chat_session` table to hold metadata
  about session.
