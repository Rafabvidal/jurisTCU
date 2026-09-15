#!/usr/bin/env bash

# Script para restauração segura do banco PostgreSQL usando Docker Compose
set -euo pipefail

DB_USER="trt6"
DB_NAME="trt6"

echo "=== Restaurando Banco de Dados PostgreSQL ==="

# Verifica se o arquivo de backup foi fornecido
if [ $# -ne 1 ]; then
    echo "❌ Erro: Caminho do arquivo de backup não especificado."
    echo "Uso: $0 <caminho_para_o_backup.sql>"
    exit 1
fi

BACKUP_FILE="$1"

# Verifica se o arquivo de backup existe no host
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo de backup '$BACKUP_FILE' não encontrado."
    exit 1
fi

# Verifica se o container do postgres está rodando
if ! docker compose ps postgres | grep -q "Up"; then
    echo "❌ Erro: O serviço 'postgres' não está rodando no Docker Compose!"
    exit 1
fi

echo "⚠️  AVISO: Isso irá restaurar o arquivo '$BACKUP_FILE' sobre o banco de dados '$DB_NAME'."
echo "Tem certeza que deseja continuar? (y/N)"
read -r response
if [[ ! "$response" =~ ^[yY]$ ]]; then
    echo "🛑 Operação cancelada pelo usuário."
    exit 0
fi

echo "🔄 Restaurando dados..."
if docker compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"; then
    echo "✅ Restauração concluída com sucesso no banco '$DB_NAME'!"
else
    echo "❌ Erro ao restaurar o banco de dados."
    exit 1
fi
