from typing import Dict, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

class ValidationError(Exception):
    """Exception raised for parameter validation issues."""
    pass

def validate_basic_inputs(symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> None:
    """Checks input values for structural validity."""
    if not symbol:
        raise ValidationError("Symbol is required (e.g., BTCUSDT).")
    
    if side.upper() not in ["BUY", "SELL"]:
        raise ValidationError(f"Invalid side '{side}'. Must be BUY or SELL.")
        
    if order_type.upper() not in ["MARKET", "LIMIT"]:
        raise ValidationError(f"Invalid order type '{order_type}'. Must be MARKET or LIMIT.")
        
    if quantity <= 0:
        raise ValidationError(f"Quantity must be greater than 0. Got: {quantity}")
        
    if order_type.upper() == "LIMIT":
        if price is None or price <= 0:
            raise ValidationError("Price is required and must be greater than 0 for LIMIT orders.")

def format_precision(value: float, step: float) -> str:
    """Formats float value into decimal representation matching tick/step size rules."""
    step_str = f"{step:.8f}".rstrip('0')
    precision = len(step_str.split('.')[1]) if '.' in step_str else 0
        
    val_dec = Decimal(str(value))
    step_dec = Decimal(str(step))
    
    # Calculate step intervals cleanly
    steps = (val_dec / step_dec).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    rounded = steps * step_dec
    
    return f"{rounded:.{precision}f}"

def validate_and_format_rules(
    symbol: str,
    order_type: str,
    quantity: float,
    price: float,
    exchange_info: Dict[str, Any]
) -> Tuple[str, str]:
    """Validates parameters against Binance filters and formats quantities/prices."""
    symbol = symbol.upper()
    
    # Find symbol configurations
    symbol_info = next((s for s in exchange_info.get("symbols", []) if s["symbol"] == symbol), None)
    if not symbol_info:
        raise ValidationError(f"Symbol '{symbol}' not found on Binance Testnet.")
        
    if symbol_info.get("status") != "TRADING":
        raise ValidationError(f"Symbol '{symbol}' is not actively TRADING. Status: {symbol_info.get('status')}")

    # Index filters by filterType
    filters = {f["filterType"]: f for f in symbol_info.get("filters", [])}
    
    # Price formatting and constraints (LIMIT orders only)
    formatted_price = None
    if order_type.upper() == "LIMIT":
        price_filter = filters.get("PRICE_FILTER")
        if price_filter:
            min_price = float(price_filter["minPrice"])
            max_price = float(price_filter["maxPrice"])
            tick_size = float(price_filter["tickSize"])
            
            if price < min_price or price > max_price:
                raise ValidationError(f"Price {price} is outside allowed filter boundary ({min_price} - {max_price}).")
            
            formatted_price = format_precision(price, tick_size)
        else:
            formatted_price = f"{price:.8f}".rstrip('0').rstrip('.')

    # Quantity formatting and constraints
    formatted_qty = str(quantity)
    lot_size_filter = filters.get("LOT_SIZE")
    if lot_size_filter:
        min_qty = float(lot_size_filter["minQty"])
        max_qty = float(lot_size_filter["maxQty"])
        step_size = float(lot_size_filter["stepSize"])
        
        if quantity < min_qty or quantity > max_qty:
            raise ValidationError(f"Quantity {quantity} is outside allowed filter boundary ({min_qty} - {max_qty}).")
            
        formatted_qty = format_precision(quantity, step_size)

    return formatted_qty, formatted_price
