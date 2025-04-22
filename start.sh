#!/bin/bash

# filepath: /home/gabriel/Documentos/github/service-neurahive/setup.sh

# Função para exibir mensagens formatadas
function print_message() {
    echo -e "\n\033[1;34m$1\033[0m\n"
}

# 1. Verificar diretório
print_message "diretório atual"
pwd
ls

# 3. Instalar dependências do Python e Node.js
print_message "Instalando dependências do Python e Node.js..."
pip install -r requirements.txt
npm install

# 5. Configurar Alembic
print_message "Configurando Alembic..."
if [ ! -d "alembic" ]; then
    alembic init alembic
fi

# Atualizar o arquivo env.py
cat > alembic/env.py <<EOL
from logging.config import fileConfig
import sys
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from src.database.models import Base
from dotenv import load_dotenv

load_dotenv('../.env')

database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL não encontrada no arquivo .env")

config = context.config
config.set_main_option('sqlalchemy.url', database_url)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
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
EOL

# 6. Criar e aplicar migrações com Alembic
print_message "Criando e aplicando migrações com Alembic..."
alembic stamp head --purge
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 7. Exportar variáveis de ambiente
print_message "Exportando variáveis de ambiente..."
export $(grep -v '^#' .env | xargs)

# 8. Iniciar a aplicação
print_message "Iniciando a aplicação..."
cd src
exec uvicorn main:app --host 0.0.0.0 --port 8080
