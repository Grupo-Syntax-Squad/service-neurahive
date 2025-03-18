# service-neurahive 🍯

## Setup database

[All commands](#command-blocks)

### Install docker compose

```bash
sudo apt install docker-compose
```

### Setup container with postgres and database

```bash
docker-compose up -d
```

## Virtual enviroment

### Install python venv

```bash
sudo apt install python3.12-venv
```

### Create virtual enviroment

```bash
python3 -m venv .venv
```

### Activate virtual enviroment

```bash
source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Alembic

### Alembic init

```bash
alembic init alembic
```

### Set database URI inside of alembic.ini file

```ini
sqlalchemy.url = postgresql://postgres:password@localhost/neurahive
```

### Alembic env.py config

```python
from logging.config import fileConfig
import sys
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from src.database.models import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Alembic revision and upgrade

```bash
alembic revision --autogenerate
alembic upgrade head
```

### If you need to delete database and create again run this command

```bash
alembic stamp head --purge
```

## Run application in development mode

```
fastapi dev
```

## Commands blocks

### Setup database

```bash
sudo apt install docker-compose
docker-compose up -d
```

### Virtual enviroment

```bash
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Alembic

```bash
alembic init alembic
alembic revision --autogenerate
alembic upgrade head
alembic stamp head --purge
```
