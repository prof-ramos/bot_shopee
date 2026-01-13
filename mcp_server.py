#!/usr/bin/env python3
"""
MCP Server para API Shopee Affiliate

Este servidor expõe as funcionalidades da API Shopee como tools MCP,
permitindo que modelos de linguagem busquem produtos e gerem links.
"""

import asyncio
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from scripts.shopee_api import ShopeeAPI, ShopeeAPIError, get_tipo_loja

# Criar servidor MCP
app = Server("shopee-api-server")

# Variáveis de ambiente
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_APP_SECRET = os.getenv("SHOPEE_APP_SECRET")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Lista todas as ferramentas disponíveis."""
    return [
        Tool(
            name="buscar_produtos",
            description="Busca produtos na Shopee por palavra-chave",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Palavra-chave para busca",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número de resultados (1-500)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 500,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="buscar_produtos_loja",
            description="Busca produtos de uma loja específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "shop_id": {
                        "type": "integer",
                        "description": "ID da loja",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número de resultados (1-500)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 500,
                    },
                },
                "required": ["shop_id"],
            },
        ),
        Tool(
            name="gerar_link_afiliado",
            description="Gera link curto de afiliado para URL da Shopee",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL completa do produto Shopee",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="verificar_credenciais",
            description="Verifica se as credenciais da API estão configuradas",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Executa uma ferramenta."""

    # Verificar credenciais antes de qualquer operação
    if not SHOPEE_APP_ID or not SHOPEE_APP_SECRET:
        if name == "verificar_credenciais":
            return [TextContent(
                type="text",
                text="❌ Credenciais não configuradas. Defina SHOPEE_APP_ID e SHOPEE_APP_SECRET."
            )]
        return [TextContent(
            type="text",
            text="Erro: Credenciais da API não configuradas. Use SHOPEE_APP_ID e SHOPEE_APP_SECRET."
        )]

    api = None
    try:
        api = ShopeeAPI()

        if name == "buscar_produtos":
            keyword = arguments.get("keyword", "")
            limit = arguments.get("limit", 10)

            produtos = await asyncio.to_thread(api.buscar_produtos, keyword=keyword, limit=limit)

            if not produtos:
                return [TextContent(type="text", text=f"Nenhum produto encontrado para '{keyword}'")]

            resultado = f"📦 {len(produtos)} produtos encontrados para '{keyword}':\n\n"
            for p in produtos[:20]:  # Limitar a 20 para não sobrecarregar
                nome = p.get("productName", "N/A")
                preco = p.get("price", "N/A")

                # Tratar conversão segura de commissionRate
                try:
                    rate = p.get("commissionRate")
                    if rate is None:
                        rate = "0"
                    comissao = float(rate) * 100
                except (ValueError, TypeError):
                    comissao = 0.0
                loja = p.get("shopName", "N/A")
                tipo = get_tipo_loja(p.get("shopType") or [])
                link = p.get("offerLink", "N/A")

                resultado += f"• {nome}\n"
                resultado += f"  💰 Preço: R$ {preco}\n"
                resultado += f"  💵 Comissão: {comissao:.1f}%\n"
                resultado += f"  🏪 {loja}"
                if tipo:
                    resultado += f" ({tipo})"
                resultado += f"\n  🔗 {link}\n\n"

            if len(produtos) > 20:
                resultado += f"... e mais {len(produtos) - 20} produtos"

            return [TextContent(type="text", text=resultado)]

        elif name == "buscar_produtos_loja":
            shop_id = arguments.get("shop_id")
            limit = arguments.get("limit", 10)

            produtos = await asyncio.to_thread(api.buscar_produtos, shop_id=shop_id, limit=limit)

            if not produtos:
                return [TextContent(type="text", text=f"Nenhum produto encontrado para loja {shop_id}")]

            resultado = f"📦 {len(produtos)} produtos da loja {shop_id}:\n\n"
            for p in produtos[:20]:
                nome = p.get("productName", "N/A")
                preco = p.get("price", "N/A")
                link = p.get("offerLink", "N/A")

                resultado += f"• {nome}\n"
                resultado += f"  💰 Preço: R$ {preco}\n"
                resultado += f"  🔗 {link}\n\n"

            if len(produtos) > 20:
                resultado += f"... e mais {len(produtos) - 20} produtos"

            return [TextContent(type="text", text=resultado)]

        elif name == "gerar_link_afiliado":
            url = arguments.get("url", "")

            link_curto = await asyncio.to_thread(api.gerar_link_curto, url)

            return [TextContent(
                type="text",
                text=f"🔗 Link de afiliado gerado:\n{link_curto}"
            )]

        elif name == "verificar_credenciais":
            return [TextContent(
                type="text",
                text="✅ Credenciais configuradas corretamente.\nAPP_ID: ****\nAPP_SECRET: ****"
            )]

        else:
            return [TextContent(type="text", text=f"Ferramenta desconhecida: {name}")]

    except ShopeeAPIError as e:
        return [TextContent(type="text", text=f"Erro da API Shopee: {e}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Erro de validação: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro inesperado: {e}")]
    finally:
        if api is not None:
            api.close()


async def main():
    """Função principal do servidor MCP."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
