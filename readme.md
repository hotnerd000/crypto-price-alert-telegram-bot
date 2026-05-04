# 🚀 Crypto Price Alert Telegram Bot

A production-ready Telegram bot that tracks cryptocurrency prices, sends alerts, and estimates swap costs across multiple networks.

---

## ✨ Features

### 📊 Price Tracking
- Get real-time crypto prices in USD
- Supports major coins (BTC, ETH, BNB, TON, etc.)

### 🔔 Smart Alerts
- Set price alerts with:
  - Take-Profit (TP)
  - Stop-Loss (SL)
- Configurable check intervals
- One active alert per coin per user

### 💸 Swap Cost Estimation
- Estimate trading cost before executing a swap
- Includes:
  - Network fee (ETH / BSC / TON)
  - Slippage (based on trade size)
  - Total cost
  - Estimated received amount

### ⚡ Efficient Architecture
- Async (non-blocking)
- Batched API calls
- SQLite database
- Config-driven design

---

## 🧠 Commands

### 📊 Get Price

/price <symbol> [amount]

Examples:
/price BTC
/price ETH 1000

---

### 🔔 Add Alert

/add <symbol> <tp> <sl> <interval_seconds>

Example:
/add BTC 70000 63000 60

---

### 📋 List Alerts

/list

---

### ❌ Remove Alert

/remove <symbol>

---

### 🔄 Update Alert

/update <symbol> <tp> <sl> <interval>

---

## 📈 Swap Estimation Model

Total Cost ≈ Network Fee + Slippage

### Network Fees (Estimated)

- ETH: $3 – $8
- BSC: $0.1 – $0.3
- TON: $0.005 – $0.02

### Slippage Model

- < $100 → 0.2%
- < $1,000 → 0.5%
- < $10,000 → 1.0%
- > $10,000 → 2.0%

---

## 🗂️ Project Structure
```
project/
├── main.py
├── handlers.py
├── price_service.py
├── db.py
├── config.py
└── requirements.txt
```
---

## ⚙️ Configuration

Example config.py:

symbol_map = {
    "btc": {"id": "bitcoin", "chain": "ETH"},
    "eth": {"id": "ethereum", "chain": "ETH"},
    "bnb": {"id": "binancecoin", "chain": "BSC"},
    "ton": {"id": "the-open-network", "chain": "TON"}
}

NETWORK_FEES = {
    "ETH": (3, 8),
    "BSC": (0.1, 0.3),
    "TON": (0.005, 0.02)
}

---

## 🛠️ Installation

1. Clone repo:
git clone <your-repo>
cd <your-repo>

2. Install dependencies:
pip install -r requirements.txt

3. Set Telegram Bot Token:
BOT_TOKEN=your_telegram_bot_token

4. Run bot:
python main.py

---

## 📦 requirements.txt

python-telegram-bot==21.0
aiohttp
aiosqlite
python-dotenv

---

## ⚠️ Disclaimer

- This bot provides estimates only
- Not financial advice
- Always verify before trading

---

## 🧑‍💻 Author

Built as part of an AI Crypto Developer project

---

## ⭐ If you like this project

Give it a star and keep building 🚀
