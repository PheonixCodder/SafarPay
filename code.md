# Project Structure

```
├── libs
│   └── platform
│       ├── src
│       │   └── sp
│       │       ├── __pycache__
│       │       ├── core
│       │       │   ├── __pycache__
│       │       │   ├── observability
│       │       │   ├── __init__.py
│       │       │   └── config.py
│       │       ├── infrastructure
│       │       │   ├── __pycache__
│       │       │   ├── cache
│       │       │   ├── db
│       │       │   ├── messaging
│       │       │   ├── security
│       │       │   └── __init__.py
│       │       └── __init__.py
│       └── pyproject.toml
├── migrations
│   ├── versions
│   │   └── __init__.py
│   ├── alembic.ini
│   └── env.py
├── scripts
│   └── init-schemas.sql
├── services
│   ├── auth
│   │   ├── auth
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __pycache__
│   │   │   │   ├── messaging
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   └── whatsapp.py
│   │   │   │   ├── security
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   ├── google_oauth.py
│   │   │   │   │   └── rate_limit.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── bidding
│   │   ├── bidding
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── gateway
│   │   ├── gateway
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── geospatial
│   │   ├── geospatial
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── location
│   │   ├── location
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── notification
│   │   ├── notification
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── ride
│   │   ├── ride
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── geospatial_client.py
│   │   │   │   ├── notification_client.py
│   │   │   │   ├── orm_models.py
│   │   │   │   ├── repositories.py
│   │   │   │   ├── webhook_client.py
│   │   │   │   └── websocket_manager.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   └── verification
│       ├── verification
│       │   ├── __pycache__
│       │   ├── api
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   └── router.py
│       │   ├── application
│       │   │   ├── __pycache__
│       │   │   ├── services
│       │   │   │   ├── identity_verification_engine.py
│       │   │   │   └── rejection_resolver.py
│       │   │   ├── __init__.py
│       │   │   ├── schemas.py
│       │   │   └── use_cases.py
│       │   ├── domain
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py
│       │   │   ├── interfaces.py
│       │   │   └── models.py
│       │   ├── infrastructure
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   ├── dependencies.py
│       │   │   ├── orm_models.py
│       │   │   ├── repositories.py
│       │   │   └── storage.py
│       │   ├── __init__.py
│       │   └── main.py
│       └── pyproject.toml
├── architecture_audit_report.md
├── code.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.migrate
├── main.py
├── pyproject.toml
├── README.md
├── Refactoring SafarPay Microservices Architecture.md
├── Tech Stack.txt
└── uv.lock
```

