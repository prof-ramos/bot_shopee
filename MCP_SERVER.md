# MCP Server - API Shopee Affiliate

Este é um servidor MCP (Model Context Protocol) que expõe as funcionalidades da API de Afiliados da Shopee Brasil como ferramentas que podem ser usadas por modelos de linguagem.

## Instalação

```bash
pip install -e .
```

Ou usando uv:
```bash
uv pip install -e .
```

**Requisitos**: Python 3.10+

## Configuração

⚠️ **AVISO**: Nunca commite o arquivo .env. Adicione `.env` ao `.gitignore`. Use variáveis de ambiente do sistema ou secret stores.

Defina as variáveis de ambiente da API Shopee:

```bash
export SHOPEE_APP_ID="seu_app_id"
export SHOPEE_APP_SECRET="sua_chave_secreta"
```

Ou crie um arquivo `.env`:
```bash
SHOPEE_APP_ID=seu_app_id
SHOPEE_APP_SECRET=sua_chave_secreta
```

## Uso

### Executar o servidor MCP

```bash
python mcp_server.py
```

### Ferramentas Disponíveis

| Ferramenta | Descrição |
|------------|-----------|
| `buscar_produtos` | Busca produtos por palavra-chave |
| `buscar_produtos_loja` | Busca produtos de uma loja específica |
| `gerar_link_afiliado` | Gera link curto de afiliado |
| `verificar_credenciais` | Verifica se as credenciais estão configuradas |

### Exemplo de Uso com Claude Desktop

Adicione ao seu arquivo de configuração do Claude Desktop:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "shopee": {
      "command": "python",
      "args": ["/caminho/para/bot_shopee/mcp_server.py"],
      "env": {
        "SHOPEE_APP_ID": "${env:SHOPEE_APP_ID}",
        "SHOPEE_APP_SECRET": "${env:SHOPEE_APP_SECRET}"
      }
    }
  }
}
```

## Exemplos de Uso

### Buscar produtos

```
Use a ferramenta buscar_produtos com keyword "celular" e limit 5
```

### Gerar link de afiliado

```
Use a ferramenta gerar_link_afiliado com a URL do produto
```

## Development

### Executar testes

```bash
python -m unittest tests.test_shopee_api -v
```

### Testar o servidor MCP manualmente

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py
```

## Rate Limits

- **2000 requisições/hora**
- **scrollId válido por 30 segundos** (para paginação)
- **Relatórios disponíveis apenas para últimos 3 meses**

## Referências

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [API Shopee Affiliate](https://open-api.affiliate.shopee.com.br/)
- [docs.md](./docs.md) - Documentação completa da API
