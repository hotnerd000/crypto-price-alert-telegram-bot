import asyncio
import time
from db import get_alerts, update_last_checked, mark_triggered
from price_service import fetch_price
from config import CHECK_INTERVAL
from db import reset_trigger, set_cooldown

BUFFER = 0.005  # 0.5%

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
                    triggered,
                    cooldown_until
                ) = alert

                if now - last_checked < interval:
                    continue

                if now < cooldown_until:
                    continue

                try:
                    price = await fetch_price(coin_id)

                    tp_buffer = tp * (1 + BUFFER)
                    sl_buffer = sl * (1 - BUFFER)

                    if price >= tp_buffer:
                        if not triggered:
                            await self.bot.send_message(
                                user_id,
                                f"🚀 {symbol.upper()} TP HIT!\nPrice: ${price}"
                            )
                            await mark_triggered(alert_id)
                            await set_cooldown(alert_id, now + 60)

                    elif price <= sl_buffer:
                        if not triggered:
                            await self.bot.send_message(
                                user_id,
                                f"⚠️ {symbol.upper()} SL HIT!\nPrice: ${price}"
                            )
                            await mark_triggered(alert_id)
                            await set_cooldown(alert_id, now + 60)

                    elif sl < price < tp:
                        if triggered:
                            await reset_trigger(alert_id)

                    await update_last_checked(alert_id, now)

                except Exception as e:
                    print("Error:", e)

            await asyncio.sleep(CHECK_INTERVAL)