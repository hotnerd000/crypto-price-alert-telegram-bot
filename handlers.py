from telegram import Update
from telegram.ext import ContextTypes
from price_service import resolve_symbol, fetch_price_single, generate_chart
from db import upsert_alert, get_user_alerts, delete_alert, get_alert_by_user_coin
from messages import HELP_ADD, CMD_UPDATE_EXAMPLE, CMD_PRICE_EXAMPLE
from price_service import generate_candlestick_chart
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def recommend_levels(price):
    return round(price * 1.05, 2), round(price * 0.95, 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Welcome!\nUse {HELP_ADD}"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0]
        tp = float(context.args[1])
        sl = float(context.args[2])
        interval = int(context.args[3])

        coin_id = resolve_symbol(symbol)

        if not coin_id:
            await update.message.reply_text("❌ Invalid symbol")
            return

        price = await fetch_price_single(coin_id)
        print(f"[DEBUG] coin_id={coin_id}, price={price}")

        if price is None:
            await update.message.reply_text("❌ Failed to fetch price.")
            return
        rec_tp, rec_sl = recommend_levels(price)

        existing = await get_alert_by_user_coin(update.effective_user.id, coin_id)        
        print("Existing---", existing)
        await upsert_alert(
            update.effective_user.id,
            symbol,
            coin_id,
            tp,
            sl,
            interval
        )

        if existing:
            old_tp = existing[4]
            old_sl = existing[5]
            old_interval = existing[6]

            msg = (
                f"🔄 Alert updated for {symbol.upper()}\n"
                f"Old → TP:{old_tp}, SL:{old_sl}, Int:{old_interval}s\n"
                f"New → TP:{tp}, SL:{sl}, Int:{interval}s"
            )
        else:
            msg = "➕ New alert created"

        await update.effective_message.reply_text(
            f"{msg} for {symbol.upper()}\n"
            f"TP: {tp}, SL: {sl}, Interval: {interval}s"
        )

    except:
        await update.message.reply_text(
            f"Usage:\n{HELP_ADD}"
        )

async def update_alert_cmd(update, context):
    if len(context.args) < 4:
        await update.effective_message.reply_text(
            "⚠️ Invalid format.\n\n"
            "Usage:\n"
            "/update <symbol> <tp> <sl> <interval>\n\n"
            "Example:\n"
            f"{CMD_UPDATE_EXAMPLE}"
        )
        return
     
    user_id = update.effective_user.id

    try:
        symbol = context.args[0].lower()
        tp = float(context.args[1])
        sl = float(context.args[2])
        interval = int(context.args[3])
    except ValueError:
        await update.effective_message.reply_text(
            "⚠️ Invalid number format.\n\n"
            "Example:\n"
            f"{CMD_UPDATE_EXAMPLE}"
        )
        return    

    coin_id = resolve_symbol(symbol)

    if not coin_id:
        await update.message.reply_text("❌ Invalid symbol.")
        return

    await upsert_alert(user_id, symbol, coin_id, tp, sl, interval)

    await update.message.reply_text(f"🔄 Alert updated for {symbol.upper()}")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
     
    if len(context.args) < 1:
        await update.effective_message.reply_text(
            f"Usage:\n/{CMD_PRICE_EXAMPLE}"
        )
        return
     
    symbol = context.args[0]
    coin_id = resolve_symbol(symbol)

    if not coin_id:
        await update.message.reply_text("❌ Invalid symbol")
        return

    price = await fetch_price_single(coin_id)
    
    print(f"[DEBUG] coin_id={coin_id}, price={price}")

    if price is None:
            await update.message.reply_text("❌ Failed to fetch price.")
            return

    alert = await get_alert_by_user_coin(update.effective_user.id, coin_id)

    msg = f"📊 {symbol.upper()} Price: ${price}"

    if alert:
        msg += (
            f"\n\n🔔 Your Alert:\n"
            f"TP: {alert[4]}\n"
            f"SL: {alert[5]}\n"
            f"Interval: {alert[6]}s"
        )

    # chart_image = await generate_chart(coin_id)
    chart = await generate_candlestick_chart(coin_id)

    # await update.effective_message.reply_photo(
    #     photo=chart,
    #     caption=msg
    # )
    chart_url = f"https://www.tradingview.com/symbols/BINANCE:{symbol.upper()}USDT/"

    keyboard = [
        [InlineKeyboardButton("📈 Chart", url=chart_url)],
        [InlineKeyboardButton("🌐 Coin Info", url=f"https://www.coingecko.com/en/coins/{coin_id}")]
    ]

    await update.effective_message.reply_photo(
        photo=chart,
        caption=msg,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def list_alerts(update, context):
    user_id = update.effective_user.id
    alerts = await get_user_alerts(user_id)

    if not alerts:
        await update.message.reply_text("📭 No alerts set.")
        return

    msg = "📊 Your Alerts:\n\n"

    for a in alerts:
        (
            alert_id,
            _,
            symbol,
            _,
            tp,
            sl,
            interval,
            _,
            triggered,
            cooldown_until
        ) = a

        status = "✅ Triggered" if triggered else "⏳ Active"

        msg += (
            f"ID: {alert_id}\n"
            f"{symbol.upper()}\n"
            f"TP: {tp} | SL: {sl}\n"
            f"Interval: {interval}s\n"
            f"Status: {status}\n\n"
        )

    await update.message.reply_text(msg)

async def remove_alert(update, context):
    try:
        alert_id = int(context.args[0])
        user_id = update.effective_user.id

        await delete_alert(alert_id, user_id)

        await update.message.reply_text(
            f"🗑️ Alert {alert_id} removed."
        )

    except:
        await update.message.reply_text(
            "Usage: /remove <alert_id>\nExample: /remove 1"
        )

