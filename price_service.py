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

    async with session.get(url) as res:
        data = await res.json()

    # Normalize output
    prices = {}
    for coin in coin_ids:
        prices[coin] = data.get(coin, {}).get("usd")

    return prices

def resolve_symbol(symbol):
    symbol = symbol.lower()
    return SYMBOL_MAP.get(symbol)