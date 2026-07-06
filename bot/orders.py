import logging
from typing import Dict, Any
from bot.client import BinanceClient, BinanceAPIError
from bot.validators import validate_basic_inputs, validate_and_format_rules

logger = logging.getLogger("trading_bot.orders")

def execute_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None
) -> Dict[str, Any]:
    """Orchestrates validation, formatting, API calling, and structured error handling."""
    logger.info(f"Preparing {order_type} {side} order on {symbol} for quantity: {quantity}")
    
    # 1. Syntax Check
    validate_basic_inputs(symbol, side, order_type, quantity, price)
    
    # 2. Dynamic Rules Setup
    logger.debug("Loading exchange information filters...")
    exchange_info = client.get_exchange_info()
    
    formatted_qty, formatted_price = validate_and_format_rules(
        symbol=symbol,
        order_type=order_type,
        quantity=quantity,
        price=price or 0.0,
        exchange_info=exchange_info
    )
    
    qty_float = float(formatted_qty)
    price_float = float(formatted_price) if formatted_price else None
    
    logger.info(f"Validated. Placing order: qty={formatted_qty}, price={formatted_price or 'MARKET'}")
    
    request_summary = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type.upper(),
        "quantity": qty_float,
        "price": price_float
    }
    
    # 3. Request execution
    try:
        res = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=qty_float,
            price=price_float
        )
        logger.info(f"Order executed. OrderId: {res.get('orderId')}")
        return {
            "success": True,
            "request": request_summary,
            "response": {
                "orderId": res.get("orderId"),
                "status": res.get("status"),
                "executedQty": res.get("executedQty"),
                "avgPrice": res.get("avgPrice") or res.get("price"),
                "raw": res
            }
        }
    except BinanceAPIError as e:
        logger.error(f"Binance API execution error: {e}")
        return {
            "success": False,
            "request": request_summary,
            "error_type": "API_ERROR",
            "message": e.message,
            "code": e.code
        }
    except ConnectionError as e:
        logger.error(f"Network connectivity error: {e}")
        return {
            "success": False,
            "request": request_summary,
            "error_type": "NETWORK_ERROR",
            "message": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected order error: {e}")
        return {
            "success": False,
            "request": request_summary,
            "error_type": "UNEXPECTED_ERROR",
            "message": str(e)
        }
