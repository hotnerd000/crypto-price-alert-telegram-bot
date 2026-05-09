import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHECK_INTERVAL = 600  # global engine loop (seconds)
CACHE_TTL = 120  # seconds
VOLATILE_CACHE_TTL = 120  # seconds
COIN_CONFIG  = {
    "btc": {
        "id": "bitcoin",
        "chain": "ETH"   # BTC wrapped trading assumption
    },
    "eth": {
        "id": "ethereum",
        "chain": "ETH"
    },
    "bnb": {
        "id": "binancecoin",
        "chain": "BSC"
    },
    "ton": {
        "id": "the-open-network",
        "chain": "TON"
    },
    "dao": {
        "id": "dao-maker",
        "chain": "ETH"
    }
}

NETWORK_FEES = {
    "ETH": (3, 8),       # Ethereum
    "BSC": (0.1, 0.3),   # Binance Smart Chain
    "TON": (0.005, 0.02) # TON
}