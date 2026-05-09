import matplotlib.pyplot as plt
import aiohttp
import time
from config import COIN_CONFIG, NETWORK_FEES, CACHE_TTL, VOLATILE_CACHE_TTL
import pandas as pd
from io import BytesIO
import mplfinance as mpf
from ta.momentum import RSIIndicator

CACHE = {}
_VOLATILE_CACHE = {
    "data": None,
    "timestamp": 0
}

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

async def generate_chart(symbol):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=1"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()

    prices = data["prices"]

    df = pd.DataFrame(prices, columns=["time", "price"])

    plt.figure()
    plt.plot(df["price"])
    plt.title(f"{symbol.upper()} Price (24h)")
    plt.xlabel("Time")
    plt.ylabel("USD")

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()

    buf.seek(0)
    return buf

async def fetch_price_single(coin_id):
    prices = await fetch_prices_batch([coin_id])
    return prices.get(coin_id)

def resolve_symbol(symbol):
    symbol = symbol.lower()
    return COIN_CONFIG[symbol]["id"]

async def generate_candlestick_chart(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=1"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()

    # Format: [timestamp, open, high, low, close]
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close"])

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)

    # Add RSI
    rsi = RSIIndicator(close=df["close"], window=14)
    df["rsi"] = rsi.rsi()

    # Add Moving Average
    df["ma20"] = df["close"].rolling(window=20).mean()

    # Create additional plots
    apds = [
        mpf.make_addplot(df["ma20"], color="blue"),
        mpf.make_addplot(df["rsi"], panel=1, color="purple", ylabel="RSI")
    ]

    # Create image buffer
    buf = BytesIO()

    mpf.plot(
        df,
        type="candle",
        style="charles",
        addplot=apds,
        volume=False,
        panel_ratios=(3, 1),
        figscale=1.2,
        savefig=dict(fname=buf, format="png")
    )

    buf.seek(0)
    return buf

    
def estimate_slippage(amount_usd: float) -> float:
    if amount_usd < 100:
        return 0.2
    elif amount_usd < 1000:
        return 0.5
    elif amount_usd < 10000:
        return 1.0
    else:
        return 2.0
    
def estimate_swap_cost_universal(symbol: str, amount: float):
    symbol = symbol.lower()

    # 🔹 Get coin config
    coin_data = COIN_CONFIG[symbol]

    if not coin_data:
        return None

    # 🔹 Extract chain from config (replaces CHAIN_MAP)
    chain = coin_data.get("chain", "ETH")

    # 🔹 Network fee
    fee_low, fee_high = NETWORK_FEES.get(chain, (1, 5))
    avg_fee = (fee_low + fee_high) / 2

    # 🔹 Slippage
    slippage_pct = estimate_slippage(amount)
    slippage_cost = amount * slippage_pct / 100

    # 🔹 Total cost
    total_cost = avg_fee + slippage_cost
    receive = amount - total_cost

    return {
        "symbol": symbol.upper(),
        "chain": chain,
        "amount": amount,
        "gas_fee": round(avg_fee, 4),
        "slippage_pct": slippage_pct,
        "slippage_cost": round(slippage_cost, 4),
        "total_cost": round(total_cost, 4),
        "receive": round(receive, 4)
    }

async def get_most_volatile(hours="6h", limit=5):
    now = time.time()

    # ✅ cache check
    if _VOLATILE_CACHE["data"] and now - _VOLATILE_CACHE["timestamp"] < CACHE_TTL:
        data = _VOLATILE_CACHE["data"]
    else:
        url = (
            "https://api.coingecko.com/api/v3/coins/markets"
            "?vs_currency=usd"
            "&order=market_cap_desc"
            "&per_page=100"
            "&price_change_percentage=1h,24h"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        _VOLATILE_CACHE["data"] = data
        _VOLATILE_CACHE["timestamp"] = now

    bullish = []
    bearish = []

    for c in data:
        # ✅ filter low quality coins
        if c.get("market_cap", 0) < 100_000_000:
            continue

        if hours == "1h":
            change = c.get("price_change_percentage_1h_in_currency") or 0
        elif hours == "24h":
            change = c.get("price_change_percentage_24h_in_currency") or 0
        else:  # 6h (custom blend)
            c1 = c.get("price_change_percentage_1h_in_currency") or 0
            c24 = c.get("price_change_percentage_24h_in_currency") or 0
            change = (c1 * 0.5) + (c24 * 0.5)

        coin = {
            "symbol": c["symbol"].upper(),
            "price": c["current_price"],
            "change": change,
            "volatility": abs(change)
        }

        if change >= 0:
            bullish.append(coin)
        else:
            bearish.append(coin)

    bullish.sort(key=lambda x: x["volatility"], reverse=True)
    bearish.sort(key=lambda x: x["volatility"], reverse=True)

    return {
        "bullish": bullish[:limit],
        "bearish": bearish[:limit]
    }