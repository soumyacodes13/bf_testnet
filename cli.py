import os
import sys
import argparse
from dotenv import load_dotenv

# Ensure root folder is on Python load path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import execute_order
from bot.validators import ValidationError

def main():
    # Setup logger
    logger = setup_logging()

    # Define arguments
    parser = argparse.ArgumentParser(
        description="Place Market or Limit orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", type=str, required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], required=True, help="BUY or SELL")
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT"], required=True, help="MARKET or LIMIT")
    parser.add_argument("--qty", type=float, required=True, help="Order quantity")
    parser.add_argument("--price", type=float, default=None, help="Limit price (required if type is LIMIT)")

    args = parser.parse_args()

    # Pre-checks on LIMIT pricing
    if args.type.upper() == "LIMIT" and args.price is None:
        parser.error("--price is required when --type is LIMIT.")

    # Load credentials
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        print("\n[ERROR] API credentials missing!")
        print("Please configure BINANCE_API_KEY and BINANCE_SECRET_KEY inside a .env file.\n")
        logger.error("API credentials missing. Execution halted.")
        sys.exit(1)

    try:
        # Run execution
        client = BinanceClient(api_key=api_key, secret_key=secret_key)
        res = execute_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.qty,
            price=args.price
        )

        if res["success"]:
            print(f"\n[SUCCESS] Order Placed: {res['response']['orderId']}")
            print(f"Details: {res['request']['side']} {res['request']['quantity']} {res['request']['symbol']} @ {res['request']['price'] or 'MARKET'}\n")
        else:
            print(f"\n[FAILED] {res.get('error_type')}: {res.get('message')}\n")

    except ValidationError as e:
        print(f"\n[Validation Error] {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Unexpected Error] {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
