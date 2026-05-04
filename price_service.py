import aiohttp
import time
from config import SYMBOL_MAP

CACHE = {}
CACHE_TTL = 120  # seconds

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

    now = time.time()

    # ✅ Check cache first
    cached_prices = {}
    coins_to_fetch = []

    for coin in coin_ids:
        if coin in CACHE and now - CACHE[coin]["ts"] < CACHE_TTL:
            cached_prices[coin] = CACHE[coin]["price"]
        else:
            coins_to_fetch.append(coin)

    # ✅ Fetch only missing coins
    if coins_to_fetch:
        ids = ",".join(coins_to_fetch)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"

        print(f"[API CALL] {url}")

        async with session.get(url) as res:
            data = await res.json()

        for coin in coins_to_fetch:
            price = data.get(coin, {}).get("usd")

            CACHE[coin] = {
                "price": price,
                "ts": now
            }

            cached_prices[coin] = price

    return cached_prices

async def fetch_price_single(coin_id):
    prices = await fetch_prices_batch([coin_id])
    return prices.get(coin_id)

def resolve_symbol(symbol):
    symbol = symbol.lower()
    return SYMBOL_MAP.get(symbol)