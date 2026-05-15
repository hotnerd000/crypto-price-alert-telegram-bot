import matplotlib.pyplot as plt
import aiohttp
import asyncio
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

        # ⚡ Set timeout (total 10 seconds)
        timeout = aiohttp.ClientTimeout(total=10)

        try:
            async with session.get(url, timeout=timeout) as res:
                # optional: raise for HTTP errors
                res.raise_for_status()
                data = await res.json()

        except asyncio.TimeoutError:
            print(f"[ERROR] Timeout fetching prices for: {ids}")
            # mark missing coins as None
            for coin in coins_to_fetch:
                cached_prices[coin] = None
            return cached_prices

        except aiohttp.ClientError as e:
            print(f"[ERROR] HTTP error fetching prices: {e}")
            for coin in coins_to_fetch:
                cached_prices[coin] = None
            return cached_prices


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
    coin = COIN_CONFIG.get(symbol)

    if not coin:
        return None

    return coin["id"]

async def generate_candlestick_chart(coin_id):

    try:
        url = (
            f"https://api.coingecko.com/api/v3/coins/"
            f"{coin_id}/ohlc?vs_currency=usd&days=1"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:

                if res.status != 200:
                    raise Exception(f"CoinGecko API error: {res.status}")

                data = await res.json()

        # ✅ Validate response
        if not data or not isinstance(data, list):
            raise ValueError("No OHLC data returned")

        # Format:
        # [timestamp, open, high, low, close]

        df = pd.DataFrame(
            data,
            columns=["time", "open", "high", "low", "close"]
        )

        # ✅ Empty dataframe protection
        if df.empty:
            raise ValueError("Empty dataframe")

        # ✅ Convert timestamp
        df["time"] = pd.to_datetime(df["time"], unit="ms")

        # ✅ Set datetime index
        df.set_index("time", inplace=True)

        # ✅ Ensure numeric
        numeric_cols = ["open", "high", "low", "close"]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # ✅ Remove invalid rows
        df.dropna(subset=numeric_cols, inplace=True)

        # ✅ Need enough candles
        if len(df) < 5:
            raise ValueError("Not enough candle data")

        # ✅ Rename for mplfinance
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close"
        }, inplace=True)

        # =========================
        # Indicators
        # =========================

        # RSI
        rsi = RSIIndicator(close=df["Close"], window=14)
        df["RSI"] = rsi.rsi()

        # Moving Average
        df["MA20"] = df["Close"].rolling(window=20).mean()

        # =========================
        # Additional plots
        # =========================

        apds = [
            mpf.make_addplot(
                df["MA20"],
                color="blue"
            ),

            mpf.make_addplot(
                df["RSI"],
                panel=1,
                color="purple",
                ylabel="RSI"
            )
        ]

        # =========================
        # Create image buffer
        # =========================

        buf = BytesIO()

        mpf.plot(
            df,
            type="candle",
            style="charles",
            addplot=apds,
            volume=False,
            panel_ratios=(3, 1),
            figscale=1.2,
            tight_layout=True,
            savefig=dict(
                fname=buf,
                format="png",
                dpi=120
            )
        )

        buf.seek(0)

        return buf

    except Exception as e:

        import traceback

        traceback.print_exc()

        print(f"[CHART ERROR] {coin_id}: {e}")

        return None
        
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