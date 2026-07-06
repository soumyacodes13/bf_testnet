import unittest
from unittest.mock import MagicMock, patch
from bot.validators import validate_basic_inputs, format_precision, validate_and_format_rules, ValidationError
from bot.client import BinanceClient

class TestTradingBot(unittest.TestCase):

    def setUp(self):
        # Mock sync_server_time to prevent live network calls during client initialization
        self.time_sync_patcher = patch('bot.client.BinanceClient.sync_server_time')
        self.mock_sync = self.time_sync_patcher.start()

    def tearDown(self):
        self.time_sync_patcher.stop()

    def test_basic_input_validation(self):
        # Valid MARKET order
        try:
            validate_basic_inputs("BTCUSDT", "BUY", "MARKET", 0.001)
        except ValidationError:
            self.fail("validate_basic_inputs raised ValidationError unexpectedly for valid MARKET order")

        # Valid LIMIT order
        try:
            validate_basic_inputs("BTCUSDT", "SELL", "LIMIT", 0.001, 30000.0)
        except ValidationError:
            self.fail("validate_basic_inputs raised ValidationError unexpectedly for valid LIMIT order")

        # Invalid side
        with self.assertRaises(ValidationError):
            validate_basic_inputs("BTCUSDT", "HOLD", "MARKET", 0.001)

        # Invalid type
        with self.assertRaises(ValidationError):
            validate_basic_inputs("BTCUSDT", "BUY", "STOP", 0.001)

        # Negative quantity
        with self.assertRaises(ValidationError):
            validate_basic_inputs("BTCUSDT", "BUY", "MARKET", -0.001)

        # Missing price for LIMIT
        with self.assertRaises(ValidationError):
            validate_basic_inputs("BTCUSDT", "BUY", "LIMIT", 0.001)

    def test_precision_formatting(self):
        self.assertEqual(format_precision(0.12345, 0.001), "0.123")
        self.assertEqual(format_precision(1.23, 0.1), "1.2")
        self.assertEqual(format_precision(10.5, 1.0), "11")
        self.assertEqual(format_precision(12.0, 5.0), "10")
        self.assertEqual(format_precision(13.0, 5.0), "15")

    def test_client_signature(self):
        client = BinanceClient(api_key="test_api_key", secret_key="test_secret_key", base_url="mock://testnet")
        query_string = "symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=90000&timeInForce=GTC&timestamp=1577836800000"
        
        import hmac
        import hashlib
        expected_sig = hmac.new(
            b"test_secret_key",
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        self.assertEqual(client._sign(query_string), expected_sig)

    @patch("requests.get")
    def test_exchange_rules_validation(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "filters": [
                        {
                            "filterType": "PRICE_FILTER",
                            "minPrice": "1000.00",
                            "maxPrice": "100000.00",
                            "tickSize": "0.01"
                        },
                        {
                            "filterType": "LOT_SIZE",
                            "minQty": "0.001",
                            "maxQty": "100.000",
                            "stepSize": "0.001"
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        client = BinanceClient(api_key="test_api_key", secret_key="test_secret_key", base_url="mock://testnet")
        exchange_info = client.get_exchange_info()

        # Valid rules validation
        formatted_qty, formatted_price = validate_and_format_rules(
            symbol="BTCUSDT",
            order_type="LIMIT",
            quantity=0.0015,
            price=40000.005,
            exchange_info=exchange_info
        )
        self.assertEqual(formatted_qty, "0.002")
        self.assertEqual(formatted_price, "40000.01")

        # Invalid symbol validation
        with self.assertRaises(ValidationError):
            validate_and_format_rules(
                symbol="ETHUSDT",
                order_type="LIMIT",
                quantity=0.001,
                price=40000.0,
                exchange_info=exchange_info
            )

if __name__ == "__main__":
    unittest.main()
