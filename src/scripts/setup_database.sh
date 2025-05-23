#!/bin/bash

set -e  # Encerra o script se qualquer outro comando falhar

echo "Parando container 'postgres' (se estiver rodando)..."
sudo docker stop postgres || true

echo "Removendo container 'postgres' (se existir)..."
sudo docker rm postgres || true

echo "Subindo containers com Docker Compose..."
sudo docker-compose up -d

echo "Aguardando o PostgreSQL aceitar conexões..."
until sudo docker exec postgres pg_isready -U postgres > /dev/null 2>&1; do
  sleep 1
done

echo "Executando migrações com Alembic..."
alembic stamp head --purge
alembic revision --autogenerate -m "Auto migration"
alembic upgrade head

echo "Populando banco de dados com dados iniciais..."
python -m src.scripts.populate_db

echo "✅ Tudo pronto!"
