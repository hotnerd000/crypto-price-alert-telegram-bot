import aiohttp
import time
from config import SYMBOL_MAP

CACHE = {}
CACHE_TTL = 20  # seconds

async def fetch_price(coin_id):
    now = time.time()

    if coin_id in CACHE:
        price, ts = CACHE[coin_id]
        if now - ts < CACHE_TTL:
            return price

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()

    price = data[coin_id]["usd"]
    CACHE[coin_id] = (price, now)
    return price

def resolve_symbol(symbol):
    symbol = symbol.lower()
    return SYMBOL_MAP.get(symbol)