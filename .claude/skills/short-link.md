---
description: Gere um link curto de rastreamento para URL da Shopee
---

Gere um link curto de afiliado para uma URL da Shopee.

Parâmetros:
- url: URL completa do produto Shopee (obrigatório)

Execute:
```bash
python3 scripts/shopee_api.py --link "<url>"
```

Exemplo:
```bash
python3 scripts/shopee_api.py --link "https://shopee.com.br/produto-exemplo"
```

O link gerado incluirá seu tracking de afiliado.
