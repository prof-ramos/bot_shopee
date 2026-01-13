---
description: Mostre o status atual do repositório git com resumo das mudanças
---

Execute:
```bash
git status --short
echo ""
echo "--- Commits recentes ---"
git log --oneline -5 2>/dev/null || echo "Nenhum commit ainda"
```

Resuma as mudanças em andamento e indique se há arquivos para commit.
