import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add scripts directory to path to import shopee_api
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))

from shopee_api import ShopeeAPI, ShopeeAPIError, get_tipo_loja


class TestShopeeAPI(unittest.TestCase):
    def setUp(self):
        self.api = ShopeeAPI(app_id="test_id", app_secret="test_secret")

    def test_get_tipo_loja(self):
        """Testa a função get_tipo_loja que extrai a lógica de tipo de loja."""
        self.assertEqual(get_tipo_loja([1]), "Mall")
        self.assertEqual(get_tipo_loja([2]), "Star")
        self.assertEqual(get_tipo_loja([4]), "Star+")
        self.assertEqual(get_tipo_loja([1, 2]), "Mall")  # Priority check
        self.assertEqual(get_tipo_loja([4, 2]), "Star+")  # Priority check
        self.assertEqual(get_tipo_loja([]), "")
        self.assertEqual(get_tipo_loja(None), "")  # None handling

    @patch("shopee_api.requests.Session.post")
    def test_buscar_ofertas_lojas_query(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"shopOfferV2": {"nodes": []}}}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call with default sort_type
        self.api.buscar_ofertas_lojas(keyword="test")

        # Verify call args
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])
        self.assertIn("sortType: $sortType", payload["query"])
        self.assertEqual(payload["variables"]["sortType"], 2)

        # Call with custom sort_type
        self.api.buscar_ofertas_lojas(keyword="test", sort_type=1)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["variables"]["sortType"], 1)

    @patch("shopee_api.requests.Session.post")
    def test_json_decode_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError(
            "Expecting value", "doc", 0
        )
        mock_response.text = "Invalid JSON"
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with self.assertRaises(ShopeeAPIError) as cm:
            self.api.request("query")

        self.assertIn("Erro ao decodificar JSON", str(cm.exception))

    @patch("shopee_api.ShopeeAPI.request")
    def test_gerar_link_curto_success(self, mock_request):
        mock_request.return_value = {
            "generateShortLink": {"shortLink": "http://short.url"}
        }
        link = self.api.gerar_link_curto("http://original.url")
        self.assertEqual(link, "http://short.url")

    @patch("shopee_api.ShopeeAPI.request")
    def test_gerar_link_curto_failure(self, mock_request):
        """Testa falhas ao gerar link curto com valores vazios ou None."""
        # Consolidar testes de falha usando subTest
        for short_link_value in ["", None]:
            with self.subTest(short_link_value=short_link_value):
                mock_request.return_value = {"generateShortLink": {"shortLink": short_link_value}}

                with self.assertRaises(ShopeeAPIError) as cm:
                    self.api.gerar_link_curto("http://original.url")

                self.assertIn("Falha ao gerar link curto", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
