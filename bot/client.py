import time
import hmac
import hashlib
import requests
import logging
from typing import Dict, Any

class BinanceAPIError(Exception):
    """Custom exception class to catch errors returned by Binance API."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error (Code: {code}): {message}")

class BinanceClient:
    """
    Minimal direct REST API client for Binance Futures Testnet.
    """
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://testnet.binancefuture.com"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger("trading_bot.client")
        self.time_offset = 0
        self.sync_server_time()

    def sync_server_time(self) -> None:
        """Aligns local time offset with Binance server time."""
        try:
            res = requests.get(f"{self.base_url}/fapi/v1/time", timeout=10)
            res.raise_for_status()
            server_time = res.json()["serverTime"]
            self.time_offset = server_time - int(time.time() * 1000)
            self.logger.debug(f"Time synced. Local offset: {self.time_offset}ms")
        except Exception as e:
            self.logger.warning(f"Could not synchronize server time: {e}. Using local time.")

    def _sign(self, query_string: str) -> str:
        """Calculates HMAC-SHA256 signature using the secret key."""
        return hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def request(self, method: str, endpoint: str, params: Dict[str, Any] = None, signed: bool = False) -> Dict[str, Any]:
        """Performs raw GET or POST HTTP requests against Binance Testnet."""
        url = f"{self.base_url}{endpoint}"
        params = params.copy() if params else {}

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key

        if signed:
            params["timestamp"] = int(time.time() * 1000) + self.time_offset
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            params["signature"] = self._sign(query_string)

        self.logger.debug(f"API Request: {method} {url} | Params: {params}")

        try:
            if method.upper() == "POST":
                res = requests.post(url, params=params, headers=headers, timeout=15)
            else:
                res = requests.get(url, params=params, headers=headers, timeout=15)

            response_body = res.text
            if len(response_body) > 500:
                response_body = response_body[:500] + "... [TRUNCATED]"
            self.logger.debug(f"API Response Code: {res.status_code} | Body: {response_body}")

            try:
                response_json = res.json()
            except ValueError:
                response_json = {"raw": res.text}

            if res.status_code != 200:
                code = response_json.get("code", res.status_code)
                msg = response_json.get("msg", res.text)
                raise BinanceAPIError(code, msg)

            return response_json

        except requests.RequestException as e:
            self.logger.error(f"Network error connecting to {url}: {e}")
            raise ConnectionError(f"Network error communicating with Binance: {e}")

    def get_exchange_info(self) -> Dict[str, Any]:
        """Fetches dynamic lot sizes and rules details."""
        return self.request("GET", "/fapi/v1/exchangeInfo")

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> Dict[str, Any]:
        """Places a buy or sell MARKET or LIMIT order."""
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity),
        }
        if order_type.upper() == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = str(price)
            params["timeInForce"] = "GTC"

        return self.request("POST", "/fapi/v1/order", params=params, signed=True)
