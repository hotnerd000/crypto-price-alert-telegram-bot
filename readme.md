# 🚀 Crypto Price Alert Telegram Bot

A production-ready Telegram bot that monitors cryptocurrency prices and sends real-time alerts when price thresholds are hit.

---

## 📌 Features

* ✅ Add price alerts (Take-Profit / Stop-Loss)
* ✅ Real-time price monitoring
* ✅ Smart alert system (no spam, cooldown enabled)
* ✅ Batch API calls (efficient & scalable)
* ✅ In-memory caching (reduces API usage)
* ✅ SQLite database (persistent alerts)
* ✅ Manual price check command
* ✅ Symbol validation & mapping

---

## 🧠 How It Works

1. User adds an alert via Telegram
2. Bot stores alert in database
3. Background engine:

   * Fetches prices (batched)
   * Applies caching (TTL)
   * Checks TP/SL conditions
4. Sends alert when condition is met

---

## ⚙️ Tech Stack

* Python 3.10+
* python-telegram-bot (async)
* aiohttp (HTTP client)
* aiosqlite (async DB)
* CoinGecko API (price data)

---

## 📂 Project Structure

```
crypto-price-alert-bot/
│
├── main.py              # Entry point
├── handlers.py          # Telegram commands
├── alert_engine.py      # Background alert logic
├── price_service.py     # API + caching + batching
├── db.py                # Database logic
├── config.py            # Config variables
└── requirements.txt
```

---

## 🔧 Installation

### 1. Clone repo

```bash
git clone git@github.com:hotnerd000/crypto-price-alert-telegram-bot.git
cd crypto-price-alert-bot
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration

Create a `config.py` file:

```python
BOT_TOKEN = "your_telegram_bot_token"
CHECK_INTERVAL = 5  # seconds
CACHE_TTL = 10      # seconds
```

---

## ▶️ Run the Bot

```bash
python main.py
```

---

## 📱 Telegram Commands

### ➕ Add Alert

```
/add <symbol> <tp> <sl> <interval>
```

Example:

```
/add BTC 70000 65000 10
```

---

### 📊 Check Price

```
/price <symbol>
```

Example:

```
/price ETH
```

---

### 📋 List Alerts

```
/list
```

---

### ❌ Remove Alert

```
/remove <alert_id>
```

---

## 🔄 Smart Alert Logic

* Cooldown prevents repeated alerts
* Trigger resets when price returns to range
* Buffer (0.5%) avoids false breakouts

---

## ⚡ Performance Optimizations

### 1. API Batching

Fetch multiple coin prices in a single request.

### 2. Caching Layer

* TTL-based caching
* Reduces API calls drastically

### 3. Shared HTTP Session

* Connection reuse
* Lower latency

---

## ⚠️ Rate Limit Handling

CoinGecko has rate limits.

Mitigations:

* Caching (10–15 sec)
* Batch requests
* Avoid unnecessary calls

---

## 🚀 Future Improvements

* 🔌 Binance WebSocket (real-time streaming)
* 📈 Chart visualization
* 📊 Portfolio tracking
* 🔔 Custom alert conditions (RSI, MACD)
* ☁️ Deploy to cloud (AWS / VPS)
* 👥 Multi-user scaling

---

## 🧪 Debugging

Enable debug logs in `price_service.py`:

```python
print("[DEBUG] URL:", url)
print("[DEBUG] Response:", data)
```

---

## 🛠 Common Issues

### ❌ "Failed to fetch price"

* Check symbol mapping
* Verify API response
* Enable debug logs

### ❌ Rate limit exceeded

* Increase `CACHE_TTL`
* Reduce `CHECK_INTERVAL`

### ❌ Invalid symbol

* Ensure mapping exists in `SYMBOL_MAP`

---

## 🧠 Supported Coins

Uses CoinGecko IDs:

Example:

```python
SYMBOL_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "ton": "the-open-network"
}
```

---

## 📜 License

MIT License

---

## 🙌 Credits

* CoinGecko API
* python-telegram-bot

---

## 💡 Final Note

This project is designed to be:

* Beginner-friendly
* Production-ready
* Easily extendable

---

🔥 Build, experiment, and upgrade it into a full trading assistant!
