# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ambiente

As credenciais da API Shopee devem ser configuradas como variáveis de ambiente:

```bash
export SHOPEE_APP_ID="seu_app_id"
export SHOPEE_APP_SECRET="sua_chave_secreta"
```

Ou crie um arquivo `.env` (baseado em `.env.example`).

## Scripts Disponíveis

### Python

```bash
# Buscar produtos (CLI)
python scripts/shopee_api.py --keyword "celular" --limit 10
python scripts/shopee_api.py -k "celular" -l 10

# Buscar produtos de uma loja específica
python scripts/shopee_api.py --shop 1404215442 --limit 10

# Gerar link curto
python scripts/shopee_api.py --link "https://shopee.com.br/produto-exemplo"
```

### Bash (cURL)

```bash
chmod +x scripts/shopee.sh
./scripts/shopee.sh 'query { productOfferV2(limit: 5) { nodes { productName price } } }'
```

## Arquitetura

### Autenticação SHA256

A API usa autenticação personalizada que requer cálculo de assinatura SHA256:

```
Signature = SHA256(AppId + Timestamp + Payload + Secret)
```

O `Payload` é o JSON stringificado da requisição (query + variables), **sem espaços** após os dois-pontos (use `separators=(',', ':')` em Python).

**Importante**: A assinatura deve ser calculada com o payload **exatamente** como será enviado, incluindo ordem dos campos e formatação.

### Estrutura do Cliente Python (`scripts/shopee_api.py`)

- **`ShopeeAPI`**: Classe principal do cliente
  - `_calculate_signature()`: Calcula assinatura SHA256
  - `request()`: Método genérico para queries/mutations GraphQL com variáveis
  - `buscar_produtos()`: Wrapper para `productOfferV2`
  - `buscar_ofertas_lojas()`: Wrapper para `shopOfferV2`
  - `gerar_link_curto()`: Wrapper para `generateShortLink` (mutation)

- **Uso de Variáveis GraphQL**: As queries usam variáveis GraphQL (`$keyword`, `$limit`, etc) em vez de interpolação de string. Isso é mais seguro e limpo.

### Queries GraphQL

As queries principais estão em `scripts/shopee_api.py`:

- `productOfferV2`: Busca produtos com filtros (keyword, shopId, productCatId, sortType)
- `shopOfferV2`: Busca ofertas de lojas
- `generateShortLink`: Mutation para gerar links curtos de rastreamento

Documentação completa em `docs.md` e exemplos em `EXEMPLOS_USO.md`.

## Rate Limits

- **2000 requisições/hora**
- **scrollId válido por 30 segundos** (para paginação)
- **Relatórios disponíveis apenas para últimos 3 meses**

Ao exceder o rate limit, aguarde a próxima janela de tempo.

## Paginação com scrollId

Para queries com paginação (`productOfferV2`, `shopOfferV2`, `conversionReport`):

1. Primeira query retorna `scrollId` em `pageInfo`
2. Use `scrollId` nas queries subsequentes
3. **scrollId expira em 30 segundos** - faça todas as queries subsequentes dentro desse prazo

## Referências

- `docs.md`: Documentação completa da API Shopee
- `EXEMPLOS_USO.md`: Exemplos de código em Python, Bash e JavaScript
- API Explorer: https://open-api.affiliate.shopee.com.br/explorer
