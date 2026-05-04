import aiohttp
import time
from config import SYMBOL_MAP

CACHE = {}
CACHE_TTL = 20  # seconds

session = None

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session

async def fetch_prices_batch(coin_ids):
    """
    Fetch multiple coin prices in ONE request
    coin_ids = ["bitcoin", "ethereum", "solana"]
    """
    session = await get_session()
    ids = ",".join(coin_ids)

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"

    print(f"[DEBUG] Request URL: {url}")

    async with session.get(url) as res:
        print(f"[DEBUG] Status: {res.status}")  # 👈 ADD
        data = await res.json()
        print(f"[DEBUG] Response: {data}")  # 👈 ADD

    prices = {}
    for coin in coin_ids:
        price = data.get(coin, {}).get("usd")

        if price is None:
            print(f"[ERROR] No price found for: {coin}")  # 👈 ADD

        prices[coin] = price

    return prices

async def fetch_price_single(coin_id):
    prices = await fetch_prices_batch([coin_id])
    return prices.get(coin_id)

def resolve_symbol(symbol):
    symbol = symbol.lower()
    return SYMBOL_MAP.get(symbol)