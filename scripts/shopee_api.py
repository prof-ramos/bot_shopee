#!/usr/bin/env python3
"""
Cliente API Shopee Affiliate
Exemplo de uso da API de Afiliados da Shopee Brasil
"""

import hashlib
import json
import os
import sys
import time
import argparse
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Credenciais (devem ser definidas como variáveis de ambiente)
_APP_ID = os.getenv("SHOPEE_APP_ID")
_APP_SECRET = os.getenv("SHOPEE_APP_SECRET")
_ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"


class ShopeeAPIError(Exception):
    """Erro da API Shopee"""

    pass


class ShopeeAPI:
    """Cliente para a API de Afiliados da Shopee"""

    def __init__(
        self, app_id: Optional[str] = _APP_ID, app_secret: Optional[str] = _APP_SECRET
    ):
        if not app_id or not app_secret:
            raise ShopeeAPIError(
                "Credenciais ausentes. Defina SHOPEE_APP_ID e SHOPEE_APP_SECRET como variáveis de ambiente."
            )
        self.app_id = app_id
        self.app_secret = app_secret
        self.endpoint = _ENDPOINT
        self.session = requests.Session()
        self.timeout = 30

    def _calculate_signature(self, timestamp: int, payload: str) -> str:
        """
        Calcula a assinatura SHA256 para autenticação.

        Args:
            timestamp: Unix timestamp atual
            payload: Corpo da requisição JSON como string

        Returns:
            Assinatura SHA256 em hexadecimal
        """
        signature_input = f"{self.app_id}{timestamp}{payload}{self.app_secret}"
        return hashlib.sha256(signature_input.encode()).hexdigest()

    def request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz uma requisição GraphQL à API Shopee.

        Args:
            query: Query GraphQL
            variables: Variáveis opcionais para a query

        Returns:
            Dicionário com a resposta da API

        Raises:
            ShopeeAPIError: Se a requisição falhar
        """
        timestamp = int(time.time())

        # Construir payload
        payload_dict = {"query": query}
        if variables:
            # Remover valores None das variáveis
            variables_clean = {k: v for k, v in variables.items() if v is not None}
            if variables_clean:
                payload_dict["variables"] = variables_clean
        payload = json.dumps(payload_dict, separators=(",", ":"))

        # Calcular assinatura
        signature = self._calculate_signature(timestamp, payload)

        # Headers
        headers = {
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}",
            "Content-Type": "application/json",
        }

        # Fazer requisição com timeout
        try:
            response = self.session.post(
                self.endpoint, headers=headers, data=payload, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ShopeeAPIError(
                f"Erro HTTP {e.response.status_code}: {e.response.text[:200]}"
            ) from e

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ShopeeAPIError(
                f"Erro ao decodificar JSON. Status: {response.status_code}, "
                f"Conteúdo: {response.text[:200]}"
            )

        # Verificar erros na resposta
        if "errors" in data:
            errors = data.get("errors", [])
            if errors:
                error = errors[0]
                extensions = error.get("extensions", {})
                code = extensions.get("code", "UNKNOWN")
                message = extensions.get(
                    "message", error.get("message", "Erro desconhecido")
                )
                raise ShopeeAPIError(f"Erro {code}: {message}")
            else:
                raise ShopeeAPIError(f"API retornou um erro sem detalhes: {data}")

        return data.get("data", {})

    def buscar_produtos(
        self,
        keyword: str = "",
        limit: int = 10,
        sort_type: int = 2,
        shop_id: Optional[int] = None,
        product_cat_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca produtos na Shopee.

        Args:
            keyword: Palavra-chave para busca
            limit: Número de resultados (máx: 500)
            sort_type: Tipo de ordenação (1=relevância, 2=mais vendidos, 5=maior comissão)
            shop_id: Filtrar por ID da loja
            product_cat_id: Filtrar por categoria de produto

        Returns:
            Lista de produtos
        """
        # Validar limit
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            raise ValueError(f"limit deve ser entre 1 e 500, recebido: {limit}")

        # Construir query dinamicamente baseado nos parâmetros fornecidos
        query_params = [
            "keyword: $keyword",
            "limit: $limit",
            "sortType: $sortType",
        ]
        query_vars = [
            "$keyword: String",
            "$limit: Int!",
            "$sortType: Int!",
        ]

        if shop_id is not None:
            query_params.append("shopId: {}".format(shop_id))
        if product_cat_id is not None:
            query_params.append("productCatId: {}".format(product_cat_id))

        query_params_str = "                ".join(query_params)
        query_vars_str = "            ".join(query_vars)

        query = """
        query ProductOfferV2(
            {vars}
        ) {{
            productOfferV2(
                {params}
            ) {{
                nodes {{
                    itemId
                    productName
                    price
                    priceMin
                    priceMax
                    commissionRate
                    commission
                    sales
                    ratingStar
                    priceDiscountRate
                    imageUrl
                    productLink
                    offerLink
                    shopId
                    shopName
                    shopType
                }}
                pageInfo {{
                    page
                    limit
                    hasNextPage
                }}
            }}
        }}
        """.format(vars=query_vars_str, params=query_params_str)

        variables = {
            "keyword": keyword or None,
            "limit": limit,
            "sortType": sort_type,
        }

        data = self.request(query, variables)
        return data.get("productOfferV2", {}).get("nodes", [])

    def buscar_ofertas_lojas(
        self,
        keyword: str = "",
        limit: int = 10,
        shop_type: Optional[List[int]] = None,
        sort_type: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Busca ofertas de lojas.

        Args:
            keyword: Nome da loja
            limit: Número de resultados
            shop_type: Tipos de loja ([1]=Mall, [2]=Star, [4]=Star+)
            sort_type: Tipo de ordenação (default: 2)

        Returns:
            Lista de ofertas de lojas
        """
        query = """
        query ShopOfferV2(
            $keyword: String
            $limit: Int!
            $shopType: [Int]
            $sortType: Int!
        ) {
            shopOfferV2(
                keyword: $keyword
                limit: $limit
                shopType: $shopType
                sortType: $sortType
            ) {
                nodes {
                    shopId
                    shopName
                    commissionRate
                    offerLink
                    ratingStar
                    remainingBudget
                }
                pageInfo {
                    page
                    hasNextPage
                }
            }
        }
        """

        variables = {
            "keyword": keyword or None,
            "limit": limit,
            "shopType": shop_type,
            "sortType": sort_type,
        }

        data = self.request(query, variables)
        return data.get("shopOfferV2", {}).get("nodes", [])

    def gerar_link_curto(
        self, origin_url: str, sub_ids: Optional[List[str]] = None
    ) -> str:
        """
        Gera um link curto de rastreamento.

        Args:
            origin_url: URL original do produto
            sub_ids: Sub IDs para tracking (até 5)

        Returns:
            Link curto gerado
        """
        # Validar URL
        if not origin_url or not isinstance(origin_url, str):
            raise ValueError("origin_url deve ser uma string não-vazia")
        if not origin_url.startswith(("http://", "https://")):
            raise ValueError("origin_url deve começar com http:// ou https://")

        # Validar sub_ids
        if sub_ids is not None:
            if not isinstance(sub_ids, list):
                raise ValueError("sub_ids deve ser uma lista")
            if len(sub_ids) > 5:
                raise ValueError("sub_ids pode ter no máximo 5 itens")

        mutation = """
        mutation GenerateShortLink($input: GenerateShortLinkInput!) {
            generateShortLink(input: $input) {
                shortLink
            }
        }
        """
        variables = {"input": {"originUrl": origin_url, "subIds": sub_ids or []}}

        data = self.request(mutation, variables)
        short_link = data.get("generateShortLink", {}).get("shortLink", "")

        if not short_link:
            raise ShopeeAPIError(f"Falha ao gerar link curto. Resposta: {data}")

        return short_link

    def __enter__(self):
        """Suporte para context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager - fecha a sessão."""
        self.close()
        return False  # Não suprime exceções

    def close(self):
        """Fecha a sessão HTTP para liberar recursos."""
        if self.session:
            self.session.close()


def get_tipo_loja(shop_type_list: Optional[List[int]]) -> str:
    """
    Retorna o tipo de loja baseado nos shopType.

    Args:
        shop_type_list: Lista de tipos de loja da API Shopee

    Returns:
        String com tipo: "Mall", "Star+", "Star" ou ""
    """
    if not shop_type_list:
        return ""
    if 1 in shop_type_list:
        return "Mall"
    if 4 in shop_type_list:
        return "Star+"
    if 2 in shop_type_list:
        return "Star"
    return ""


def main():
    """Exemplo de uso da API"""

    parser = argparse.ArgumentParser(description="Shopee Affiliate API Client")
    parser.add_argument("--keyword", "-k", help="Palavra-chave para busca")
    parser.add_argument(
        "--limit", "-l", type=int, default=10, help="Número de resultados"
    )
    parser.add_argument("--shop", "-s", type=int, help="ID da loja")
    parser.add_argument("--link", help="Gerar link curto para URL")

    args = parser.parse_args()

    try:
        with ShopeeAPI() as api:
            if args.link:
                # Gerar link curto
                link = api.gerar_link_curto(args.link)
                print(f"🔗 Link curto: {link}")

            else:
                # Buscar produtos
                produtos = api.buscar_produtos(
                    keyword=args.keyword or "", limit=args.limit, shop_id=args.shop
                )

                print(f"\n📦 {len(produtos)} produtos encontrados:\n")

                for i, p in enumerate(produtos, 1):
                    comissao_pct = float(p.get("commissionRate", "0")) * 100
                    loja_tipo = p.get("shopType") or []

                    tipo_str = get_tipo_loja(loja_tipo)

                    print(f"{i}. {p.get('productName', 'N/A')}")
                    print(f"   💰 Preço: R$ {p.get('price', 'N/A')}")
                    print(
                        f"   💵 Comissão: {comissao_pct:.1f}% (R$ {p.get('commission', 'N/A')})"
                    )
                    print(f"   🛒 Vendidos: {p.get('sales', 0)}")
                    print(f"   ⭐ Avaliação: {p.get('ratingStar', 'N/A')}")
                    if tipo_str:
                        print(f"   🏪 {tipo_str}")
                    print(f"   🔗 {p.get('offerLink', 'N/A')}")
                    print()
    except ShopeeAPIError as e:
        print(f"❌ Erro da API: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de rede: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
