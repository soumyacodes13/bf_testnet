# Binance Futures Testnet Trading Bot

A minimal, high-quality Python bot for placing Market and Limit orders on the Binance Futures Testnet (USDT-M). Includes dynamic exchange-rule validations, clean console/file logging, and a lightweight web interface.

---

## ⚡ Quick Start

### 1. Installation
Install the minimal dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory (do not commit this to GitHub) and add your testnet keys:
```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_SECRET_KEY=your_testnet_secret_key
```
*A template is available in `.env.example`.*

---

## 🚀 How to Run

### Option A: Web UI (Recommended)
Launch the lightweight local web page:
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

### Option B: Command Line Interface (CLI)
You can also run orders directly from your terminal:

*   **Market Buy:**
    ```bash
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.005
    ```
*   **Limit Sell:**
    ```bash
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.002 --price 62000.00
    ```

---

## 🧪 Running Tests
To verify local constraints, decimal precision rounding, and cryptographic HMAC signatures:
```bash
python test_bot.py
```

