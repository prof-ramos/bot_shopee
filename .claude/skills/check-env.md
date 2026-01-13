---
description: Verifique se as variáveis de ambiente da API Shopee estão configuradas
---

Verifique se as credenciais da API Shopee estão configuradas.

Execute:
```bash
echo "SHOPEE_APP_ID: ${SHOPEE_APP_ID:+configured}"
echo "SHOPEE_APP_SECRET: ${SHOPEE_APP_SECRET:+configured}"
echo "SHOPEE_ENDPOINT: ${SHOPEE_ENDPOINT:+${SHOPEE_ENDPOINT}}"

# Verificar também arquivo .env
if [ -f .env ]; then
    echo ""
    echo "Variáveis no .env:"
    grep -E "^SHOPEE_" .env | sed 's/=.*/=***/'
else
    echo "Arquivo .env não encontrado"
fi
```

Se as variáveis não estiverem configuradas, oriente o usuário a:
1. Criar um arquivo .env baseado em .env.example
2. Definir SHOPEE_APP_ID e SHOPEE_APP_SECRET
