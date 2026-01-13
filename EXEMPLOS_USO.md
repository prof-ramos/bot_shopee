# Guia de Uso da API Shopee Affiliate

Exemplos práticos de como integrar com a API Shopee Affiliate.

---

## Configuração Inicial

### Credenciais

- **AppID**: `18360190851`
- **Secret**: `EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C`
- **Endpoint**: `https://open-api.affiliate.shopee.com.br/graphql`

---

## Exemplo 1: Python

### Instalação de dependências

```bash
pip install requests
```

### Código Python

```python
import hashlib
import json
import time
import requests

# Credenciais
APPID = "18360190851"
SECRET = "EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C"
ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

def calcular_assinatura(appid: str, timestamp: int, payload: str, secret: str) -> str:
    """
    Calcula a assinatura SHA256 para autenticação.

    Fórmula: SHA256(AppId + Timestamp + Payload + Secret)
    """
    signature_input = f"{appid}{timestamp}{payload}{secret}"
    return hashlib.sha256(signature_input.encode()).hexdigest()

def fazer_requisicao(query: str):
    """
    Faz uma requisição à API Shopee Affiliate.
    """
    timestamp = int(time.time())
    payload = json.dumps({"query": query})

    # Calcular assinatura
    signature = calcular_assinatura(APPID, timestamp, payload, SECRET)

    # Headers
    headers = {
        "Authorization": f"SHA256 Credential={APPID}, Timestamp={timestamp}, Signature={signature}",
        "Content-Type": "application/json"
    }

    # Fazer requisição
    response = requests.post(ENDPOINT, headers=headers, data=payload)
    response.raise_for_status()

    return response.json()

# Exemplo 1: Buscar produtos
query_produtos = """
query {
    productOfferV2(limit: 5) {
        nodes {
            itemId
            productName
            price
            commissionRate
            commission
            sales
            offerLink
        }
        pageInfo {
            page
            limit
            hasNextPage
        }
    }
}
"""

resultado = fazer_requisicao(query_produtos)
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Exibir produtos formatados
for produto in resultado["data"]["productOfferV2"]["nodes"]:
    print(f"\n📦 {produto['productName']}")
    print(f"   💰 Preço: R$ {produto['price']}")
    print(f"   💵 Comissão: {float(produto['commissionRate'])*100:.1f}% (R$ {produto['commission']})")
    print(f"   🛒 Vendidos: {produto['sales']}")
    print(f"   🔗 Link: {produto['offerLink']}")
```

---

## Exemplo 2: cURL (Bash)

### Script Bash

```bash
#!/bin/bash

APPID="18360190851"
SECRET="EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C"
ENDPOINT="https://open-api.affiliate.shopee.com.br/graphql"

# Obter timestamp atual
TIMESTAMP=$(date +%s)

# Payload da query (deve estar em uma única linha)
PAYLOAD='{"query":"query { productOfferV2(limit: 5) { nodes { itemId productName price commissionRate offerLink } } }"}'

# Calcular assinatura
SIGNATURE_INPUT="${APPID}${TIMESTAMP}${PAYLOAD}${SECRET}"
SIGNATURE=$(echo -n "$SIGNATURE_INPUT" | openssl dgst -sha256 -hex | awk '{print $2}')

# Fazer requisição
curl -s -X POST "$ENDPOINT" \
  -H "Authorization: SHA256 Credential=$APPID, Timestamp=$TIMESTAMP, Signature=$SIGNATURE" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" | python3 -m json.tool
```

### cURL One-liner

```bash
APPID="18360190851"; SECRET="EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C"; TS=$(date +%s); \
PAYLOAD='{"query":"query { productOfferV2(limit: 3) { nodes { productName price commissionRate } } }"}'; \
SIG=$(echo -n "${APPID}${TS}${PAYLOAD}${SECRET}" | openssl dgst -sha256 -hex | awk '{print $2}'); \
curl -s -X POST 'https://open-api.affiliate.shopee.com.br/graphql' \
  -H "Authorization: SHA256 Credential=$APPID, Timestamp=$TS, Signature=$SIG" \
  -H 'Content-Type: application/json' -d "$PAYLOAD" | jq
```

---

## Exemplo 3: Node.js / JavaScript

### Instalação de dependências

```bash
npm install node-fetch
# ou
npm install axios
```

### Código JavaScript (com fetch)

```javascript
const crypto = require('crypto');

// Credenciais
const APPID = '18360190851';
const SECRET = 'EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C';
const ENDPOINT = 'https://open-api.affiliate.shopee.com.br/graphql';

/**
 * Calcula a assinatura SHA256 para autenticação
 */
function calcularAssinatura(appid, timestamp, payload, secret) {
    const signatureInput = `${appid}${timestamp}${payload}${secret}`;
    return crypto.createHash('sha256').update(signatureInput).digest('hex');
}

/**
 * Faz uma requisição à API Shopee Affiliate
 */
async function fazerRequisicao(query) {
    const timestamp = Math.floor(Date.now() / 1000);
    const payload = JSON.stringify({ query });

    // Calcular assinatura
    const signature = calcularAssinatura(APPID, timestamp, payload, SECRET);

    // Headers
    const headers = {
        'Authorization': `SHA256 Credential=${APPID}, Timestamp=${timestamp}, Signature=${signature}`,
        'Content-Type': 'application/json'
    };

    // Fazer requisição
    const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers,
        body: payload
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

// Exemplo de uso
(async () => {
    const query = `
        query {
            productOfferV2(limit: 5) {
                nodes {
                    itemId
                    productName
                    price
                    commissionRate
                    offerLink
                }
            }
        }
    `;

    try {
        const resultado = await fazerRequisicao(query);
        console.log(JSON.stringify(resultado, null, 2));

        // Exibir produtos
        resultado.data.productOfferV2.nodes.forEach(produto => {
            console.log(`\n📦 ${produto.productName}`);
            console.log(`   💰 Preço: R$ ${produto.price}`);
            console.log(`   💵 Comissão: ${(parseFloat(produto.commissionRate) * 100).toFixed(1)}%`);
            console.log(`   🔗 ${produto.offerLink}`);
        });
    } catch (erro) {
        console.error('Erro:', erro.message);
    }
})();
```

---

## Exemplo 4: Node.js com Axios

```javascript
const axios = require('axios');
const crypto = require('crypto');

const APPID = '18360190851';
const SECRET = 'EX4IKYDSUTTBJQRCCL63KCHU66HCOJ3C';

function calcularAssinatura(appid, timestamp, payload, secret) {
    const signatureInput = `${appid}${timestamp}${payload}${secret}`;
    return crypto.createHash('sha256').update(signatureInput).digest('hex');
}

async function fazerRequisicao(query) {
    const timestamp = Math.floor(Date.now() / 1000);
    const payload = JSON.stringify({ query });
    const signature = calcularAssinatura(APPID, timestamp, payload, SECRET);

    const response = await axios.post('https://open-api.affiliate.shopee.com.br/graphql',
        payload,
        {
            headers: {
                'Authorization': `SHA256 Credential=${APPID}, Timestamp=${timestamp}, Signature=${signature}`,
                'Content-Type': 'application/json'
            }
        }
    );

    return response.data;
}

// Uso
fazerRequisicao('query { productOfferV2(limit: 3) { nodes { productName price } } }')
    .then(data => console.log(JSON.stringify(data, null, 2)))
    .catch(err => console.error(err.response?.data || err.message));
```

---

## Queries Úteis

### Buscar Produtos com Filtro

```graphql
query {
    productOfferV2(
        keyword: "celular"
        sortType: 2  # ITEM_SOLD_DESC (mais vendidos)
        limit: 10
    ) {
        nodes {
            itemId
            productName
            price
            priceMin
            priceMax
            commissionRate
            commission
            sales
            ratingStar
            imageUrl
            offerLink
            shopName
            shopType
        }
        pageInfo {
            page
            limit
            hasNextPage
        }
    }
}
```

### Buscar Ofertas por Loja

```graphql
query {
    shopOfferV2(
        keyword: "Samsung"
        sortType: 2  # Maior comissão
        limit: 10
    ) {
        nodes {
            shopId
            shopName
            commissionRate
            offerLink
            ratingStar
        }
        pageInfo {
            page
            hasNextPage
        }
    }
}
```

### Gerar Link Curto (Mutation)

```graphql
mutation {
    generateShortLink(input: {
        originUrl: "https://shopee.com.br/produto-exemplo"
        subIds: ["s1", "s2", "s3", "s4", "s5"]
    }) {
        shortLink
    }
}
```

---

## Tratamento de Erros

### Erros Comuns

| Código | Erro | Solução |
|--------|------|---------|
| 10020 | Invalid Signature | Verifique o cálculo da assinatura |
| 10020 | Request Expired | Sincronize o relógio do servidor |
| 10030 | Rate limit exceeded | Aguarde antes de fazer nova requisição |
| 10032 | Invalid affiliate id | Verifique suas credenciais |

### Exemplo de Tratamento de Erros (Python)

```python
def fazer_requisicao_com_tratamento(query: str):
    try:
        resultado = fazer_requisicao(query)

        # Verificar erros na resposta
        if "errors" in resultado:
            for erro in resultado["errors"]:
                print(f"❌ Erro {erro['extensions']['code']}: {erro['extensions']['message']}")
            return None

        return resultado["data"]

    except requests.exceptions.HTTPError as e:
        print(f"❌ Erro HTTP: {e.response.status_code}")
        print(e.response.text)
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

# Uso
dados = fazer_requisicao_com_tratamento(query_produtos)
if dados:
    print("✅ Requisição bem-sucedida!")
```

---

## Rate Limit

- **Limite**: 2000 requisições por hora
- **Ao exceder**: Aguarde a próxima janela de tempo

### Exemplo de Rate Limiting (Python)

```python
import time
from functools import wraps

# Rate limiting: máximo 30 requisições por minuto
REQUESTS = []
MAX_REQUESTS_PER_MINUTE = 30

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        now = time.time()

        # Remover requisições antigas (mais de 60 segundos)
        REQUESTS[:] = [t for t in REQUESTS if now - t < 60]

        if len(REQUESTS) >= MAX_REQUESTS_PER_MINUTE:
            sleep_time = 60 - (now - REQUESTS[0])
            print(f"⏳ Rate limit atingido. Aguardando {sleep_time:.1f}s...")
            time.sleep(sleep_time)

        REQUESTS.append(time.time())
        return func(*args, **kwargs)
    return wrapper

@rate_limit
def fazer_requisicao_limitada(query):
    return fazer_requisicao(query)
```

---

## Paginação com ScrollId

### Exemplo de Paginação (Python)

```python
def buscar_todos_os_produtos(query_pagina1):
    """
    Busca todas as páginas usando scrollId.
    """
    todos_produtos = []

    # Primeira página
    dados = fazer_requisicao(query_pagina1)
    nodes = dados["data"]["productOfferV2"]["nodes"]
    todos_produtos.extend(nodes)

    page_info = dados["data"]["productOfferV2"]["pageInfo"]

    # Páginas seguintes com scrollId
    while page_info["hasNextPage"] and page_info.get("scrollId"):
        scroll_id = page_info["scrollId"]

        # Query com scrollId (válida por 30 segundos!)
        query_pagseguinte = f"""
        query {{
            productOfferV2(
                scrollId: "{scroll_id}"
                page: {page_info["page"] + 1}
                limit: 500
            ) {{
                nodes {{ itemId productName price }}
                pageInfo {{ page hasNextPage scrollId }}
            }}
        }}
        """

        dados = fazer_requisicao(query_pagseguinte)
        nodes = dados["data"]["productOfferV2"]["nodes"]
        todos_produtos.extend(nodes)
        page_info = dados["data"]["productOfferV2"]["pageInfo"]

    return todos_produtos
```

---

## Resumo

1. **Autenticação**: Use SHA256(AppId + Timestamp + Payload + Secret)
2. **Endpoint**: `https://open-api.affiliate.shopee.com.br/graphql`
3. **Rate Limit**: 2000 requisições/hora
4. **ScrollId**: Válido por 30 segundos para paginação
5. **Consultas**: Últimos 3 meses para relatórios de conversão

Para testes rápidos, use o [API Explorer](https://open-api.affiliate.shopee.com.br/explorer).
