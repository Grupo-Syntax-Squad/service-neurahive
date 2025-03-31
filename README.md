# service-neurahive 🍯

## Setup database

[All commands](#command-blocks)

### Install docker compose and start PostgreSQL
<details>
  <summary><strong>Ubuntu</strong></summary>

```bash
sudo apt install docker-compose
```
</details>

<details>
  <summary><strong>Windows</strong></summary>
  
  ```powershell
choco install docker-compose
```
</details>

<details>
  <summary><strong>Mac</strong></summary>
  
```bash
brew install docker-compose
```
</details>

##### After installed docker-compose:
```bash
docker-compose up -d
```

## Virtual enviroment

### Install python venv

<details>
  <summary><strong>Ubuntu</strong></summary>

```bash
sudo apt install python3.12-venv
```
## Install dependencies and Activate virtual enviroment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
</details>

<details>
  <summary><strong>Windows</strong></summary>

```powershell
pip install virtualenv
```
## Install dependencies and Activate virtual enviroment
```bash
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirementsWindows.txt
```
</details>

<details>
  <summary><strong>Mac</strong></summary>

```bash
brew install python@3.12
```
## Install dependencies and Activate virtual enviroment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
</details>

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

from dotenv import load_dotenv
load_dotenv('../.env')

#Configure environment variables
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL não encontrada no arquivo .env")

config = context.config
config.set_main_option('sqlalchemy.url', database_url)

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

```bash
cd src
fastapi dev
```

## Commands blocks

```bash
# Ubuntu
sudo apt install python3.12-venv
docker-compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Windows
pip install virtualenv
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

# Mac
brew install python@3.12
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

### 🗃️ Directory Structure

<div align="center">

| Directory                                | Description                                                                                 |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| :open_file_folder: src/                  | Main project directory, containing dependencies, source code, and media files.              |
| :open_file_folder: src/auth              | Authentication-related files.                                                               |
| :open_file_folder: src/database          | Database-related code.                                                                      |
| :open_file_folder: src/modules           | All project modules and communication with external services.                               |
| :open_file_folder: src/routers           | Service requests (backend server and API) via GET, POST, DELETE, and UPDATE methods.        |
| :open_file_folder: src/schemas           | Project schemas and data models.                                                            |
| :open_file_folder: src/tests             | Project tests.                                                                              |
| :page_facing_up: .env.example            | Example environment variables file.                                                         |
| :page_facing_up: .gitignore              | Specifies files and directories to be ignored by Git.                                       |
| :page_facing_up: alembic.ini             | Configuration file for Alembic migrations.                                                  |
| :page_facing_up: changelog-template.hbs  | Template file for generating changelogs.                                                    |
| :page_facing_up: CHANGELOG.md            | File containing the project's change history.                                               |
| :page_facing_up: commitlint.config.cjs   | Configuration file for commit message linting.                                              |
| :page_facing_up: docker-compose.yml      | Docker Compose configuration file.                                                          |
| :page_facing_up: package.json            | Contains project dependencies and scripts for package management.                           |
| :page_facing_up: pyproject.toml          | Configuration file for Python dependencies and tools.                                       |
| :page_facing_up: README.md               | Main documentation file for the project.                                                    |
| :page_facing_up: requirements.txt        | List of dependencies required to run the project.                                           |
| :page_facing_up: requirementsWindows.txt | List of dependencies for running the project on Windows.                                    |
| :page_facing_up: version.json            | File containing versioning information for the project.                                     |

