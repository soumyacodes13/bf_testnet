import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import execute_order
from bot.validators import ValidationError

# Ensure logging is set up
logger = setup_logging()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/order", methods=["POST"])
def place_order():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error_type": "INPUT_ERROR", "message": "No JSON payload received"}), 400

        symbol = data.get("symbol")
        side = data.get("side")
        order_type = data.get("type")
        quantity = data.get("qty")
        price = data.get("price")

        # Cast numbers properly
        quantity = float(quantity) if quantity else 0.0
        if price:
            price = float(price)

        load_dotenv()
        api_key = os.getenv("BINANCE_API_KEY")
        secret_key = os.getenv("BINANCE_SECRET_KEY")

        if not api_key or not secret_key:
            return jsonify({
                "success": False, 
                "error_type": "AUTH_ERROR", 
                "message": "API credentials missing! Please configure BINANCE_API_KEY and BINANCE_SECRET_KEY in .env."
            }), 401

        client = BinanceClient(api_key=api_key, secret_key=secret_key)
        res = execute_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )

        return jsonify(res)

    except ValidationError as e:
        return jsonify({"success": False, "error_type": "VALIDATION_ERROR", "message": str(e)}), 400
    except ValueError:
        return jsonify({"success": False, "error_type": "INPUT_ERROR", "message": "Invalid numeric value for quantity or price"}), 400
    except Exception as e:
        logger.error(f"Unexpected Web UI Error: {e}")
        return jsonify({"success": False, "error_type": "UNEXPECTED_ERROR", "message": str(e)}), 500

if __name__ == "__main__":
    # Run the Flask app on localhost, port 5000
    app.run(host="127.0.0.1", port=5000, debug=True)
