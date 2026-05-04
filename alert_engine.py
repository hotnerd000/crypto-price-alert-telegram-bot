import asyncio
import time
from db import get_alerts, update_last_checked, mark_triggered
from price_service import fetch_price
from config import CHECK_INTERVAL

class AlertEngine:
    def __init__(self, bot):
        self.bot = bot

    async def run(self):
        while True:
            alerts = await get_alerts()
            now = int(time.time())

            for alert in alerts:
                (
                    alert_id,
                    user_id,
                    symbol,
                    coin_id,
                    tp,
                    sl,
                    interval,
                    last_checked,
                    triggered
                ) = alert

                if now - last_checked < interval:
                    continue

                try:
                    price = await fetch_price(coin_id)

                    if not triggered:
                        if price >= tp:
                            await self.bot.send_message(
                                user_id,
                                f"🚀 {symbol.upper()} TP HIT!\nPrice: ${price}"
                            )
                            await mark_triggered(alert_id)

                        elif price <= sl:
                            await self.bot.send_message(
                                user_id,
                                f"⚠️ {symbol.upper()} SL HIT!\nPrice: ${price}"
                            )
                            await mark_triggered(alert_id)

                    await update_last_checked(alert_id, now)

                except Exception as e:
                    print("Error:", e)

            await asyncio.sleep(CHECK_INTERVAL)