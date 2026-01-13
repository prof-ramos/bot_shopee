# Shopee Affiliate API Bot

Integração com a API de Afiliados da Shopee Brasil para buscar produtos, ofertas e gerar links de rastreamento.

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Documentação](#documentação)
- [Rate Limits](#rate-limits)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 👁️ Visão Geral

Este projeto fornece uma interface simplificada para a API de Afiliados da Shopee Brasil, permitindo:

- Buscar produtos com filtros e ordenação
- Consultar ofertas de lojas
- Gerar links de rastreamento curtos
- Obter relatórios de conversão

## ✨ Funcionalidades

- **Buscar Produtos** - Consulta produtos com filtros por categoria, loja, palavra-chave
- **Ofertas de Lojas** - Lista ofertas por loja com filtros de tipo
- **Links Curtos** - Gera links de rastreamento para produtos
- **Relatórios** - Consulta relatórios de conversão (últimos 3 meses)
- **Paginação** - Suporte a scrollId para navegar múltiplas páginas

## 📦 Pré-requisitos

- Python 3.8+ ou Node.js 16+
- Credenciais da API Shopee Affiliate ([Solicite aqui](https://shopee.com.br/affiliate))

## 🚀 Instalação

### Clone o repositório

```bash
git clone https://github.com/seu-usuario/bot_shopee.git
cd bot_shopee
```

### Python

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install requests
```

### Node.js

```bash
# Instalar dependências
npm install axios node-fetch
```

## ⚙️ Configuração

### Credenciais

Obtenha suas credenciais no [Portal de Afiliados Shopee](https://shopee.com.br/affiliate):

- `APP_ID` - Seu AppId
- `APP_SECRET` - Sua chave secreta

### Variáveis de Ambiente (opcional)

Crie um arquivo `.env`:

```bash
SHOPEE_APP_ID=seu_app_id_aqui
SHOPEE_APP_SECRET=sua_chave_secreta_aqui
```

## 📖 Uso

### Python

```python
from shopee_api import ShopeeAPI

# Inicializar API
api = ShopeeAPI(
    app_id="seu_app_id",
    app_secret="sua_chave_secreta"
)

# Buscar produtos
produtos = api.buscar_produtos(limit=10)
for produto in produtos:
    print(f"{produto['productName']} - R$ {produto['price']}")
```

### cURL

```bash
./scripts/shopee.sh "query { productOfferV2(limit: 5) { nodes { productName price } } }"
```

### Node.js

```javascript
const { ShopeeAPI } = require('./shopee-api');

const api = new ShopeeAPI({
    appId: 'seu_app_id',
    appSecret: 'sua_chave_secreta'
});

const produtos = await api.buscarProdutos({ limit: 10 });
console.log(produtos);
```

## 📚 Documentação

- [Documentação Completa da API](docs.md) - Referência completa da API Shopee
- [Guia de Uso com Exemplos](EXEMPLOS_USO.md) - Exemplos práticos em Python, Bash e JavaScript

## ⚡ Rate Limits

A API Shopee possui os seguintes limites:

| Limite | Valor |
|--------|-------|
| Requisições por hora | 2000 |
| Diferença de timestamp | 10 minutos |
| ScrollId válido por | 30 segundos |
| Relatórios disponíveis | Últimos 3 meses |

## 🔧 Scripts Disponíveis

```bash
# Python
python scripts/buscar_produtos.py --keyword "celular" --limit 10

# Bash
./scripts/shopee.sh "{ sua_query_graphql }"

# Node.js
npm run buscar --keyword "celular"
```

## 📁 Estrutura do Projeto

```
bot_shopee/
├── docs.md                 # Documentação completa da API
├── EXEMPLOS_USO.md         # Exemplos práticos de código
├── README.md               # Este arquivo
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── scripts/                # Scripts de exemplo
│   ├── buscar_produtos.py
│   ├── shopee.sh
│   └── gerar_link.js
└── src/                    # Código fonte
    ├── __init__.py
    └── shopee_api.py
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🔗 Links Úteis

- [Shopee Affiliate Brasil](https://shopee.com.br/affiliate)
- [API Explorer](https://open-api.affiliate.shopee.com.br/explorer)
- [Documentação GraphQL](https://graphql.org/)

## 📞 Suporte

Para dúvidas sobre a API Shopee, utilize o [formulário de contato](https://help.shopee.com.br/portal/webform/bbce78695c364ba18c9cbceb74ec9091).

---

⚠️ **Aviso**: Mantenha suas credenciais (`APP_SECRET`) em segurança e nunca as commit em repositórios públicos.
