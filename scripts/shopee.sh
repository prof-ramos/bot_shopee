#!/bin/bash

# Script para fazer requisições à API Shopee Affiliate via cURL
# Uso: ./shopee.sh "query { productOfferV2(limit: 5) { nodes { productName price } } }"

# Credenciais (substitua pelas suas ou use .env)
APPID="${SHOPEE_APP_ID:-18360190851}"
SECRET="${SHOPEE_APP_SECRET:-EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C}"
ENDPOINT="https://open-api.affiliate.shopee.com.br/graphql"

# Verificar argumentos
if [ -z "$1" ]; then
    echo "Uso: $0 'query_graphql'"
    echo ""
    echo "Exemplo:"
    echo '  $0 "query { productOfferV2(limit: 5) { nodes { productName price } } }"'
    exit 1
fi

# Obter timestamp atual
TIMESTAMP=$(date +%s)

# Criar payload (escape aspas corretamente)
QUERY="$1"
PAYLOAD=$(echo "{\"query\":\"${QUERY}\"}" | sed 's/"/\\"/g')

# Calcular assinatura
SIGNATURE_INPUT="${APPID}${TIMESTAMP}${PAYLOAD}${SECRET}"
SIGNATURE=$(echo -n "$SIGNATURE_INPUT" | openssl dgst -sha256 -hex | awk '{print $2}')

echo "=== Shopee API Request ==="
echo "Timestamp: $TIMESTAMP"
echo "Query: $QUERY"
echo ""

# Fazer requisição
curl -s -X POST "$ENDPOINT" \
  -H "Authorization: SHA256 Credential=$APPID, Timestamp=$TIMESTAMP, Signature=$SIGNATURE" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" | python3 -m json.tool

echo ""
echo "=== Fim ==="
