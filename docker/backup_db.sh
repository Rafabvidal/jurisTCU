#!/usr/bin/env bash

# Script para backup seguro do banco PostgreSQL usando Docker Compose
set -euo pipefail

# Configurações padrão extraídas do compose.yaml
DB_USER="trt6"
DB_NAME="trt6"
BACKUP_FILE="backup_trt6_$(date +%Y%m%d_%H%M%S).sql"

echo "=== Iniciando Backup do Banco de Dados PostgreSQL ==="

# Verifica se o container do postgres está rodando
if ! docker compose ps postgres | grep -q "Up"; then
    echo "❌ Erro: O serviço 'postgres' não está rodando no Docker Compose!"
    echo "Por favor, inicie os containers com 'docker compose up -d' antes de rodar o backup."
    exit 1
fi

echo "💾 Gerando dump do banco '$DB_NAME' como usuário '$DB_USER'..."
# Usamos -T para desativar TTY e evitar problemas de escape de caracteres no dump redirecionado
if docker compose exec -T postgres pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"; then
    echo "✅ Backup realizado com sucesso!"
    echo "📄 Arquivo gerado: $(pwd)/$BACKUP_FILE"
    echo "📏 Tamanho do arquivo: $(du -sh "$BACKUP_FILE" | cut -f1)"
else
    echo "❌ Erro ao gerar o dump do banco de dados."
    exit 1
fi
