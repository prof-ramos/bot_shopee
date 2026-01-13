---
description: Busque produtos na API Shopee usando keyword
---

Busque produtos na Shopee usando a API de afiliados.

Parâmetros:
- keyword: palavra-chave para busca (obrigatório)
- limit: número de resultados (opcional, padrão: 10, máximo: 500)

Execute:
```bash
python3 scripts/shopee_api.py --keyword "<keyword>" --limit <limit>
```

Exemplo:
```bash
python3 scripts/shopee_api.py --keyword "celular" --limit 5
```
