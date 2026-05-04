from telegram import Update
from telegram.ext import ContextTypes
from price_service import resolve_symbol, fetch_price
from db import add_alert

def recommend_levels(price):
    return round(price * 1.05, 2), round(price * 0.95, 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome!\nUse /add BTC 70000 63000 60"
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

        price = await fetch_price(coin_id)
        rec_tp, rec_sl = recommend_levels(price)

        await add_alert(
            update.effective_user.id,
            symbol,
            coin_id,
            tp,
            sl,
            interval
        )

        await update.message.reply_text(
            f"✅ Alert added\n"
            f"Current: ${price}\n"
            f"Your TP: {tp}, SL: {sl}\n"
            f"Suggested TP: {rec_tp}, SL: {rec_sl}"
        )

    except:
        await update.message.reply_text(
            "Usage:\n/add BTC 70000 63000 60"
        )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0]
        coin_id = resolve_symbol(symbol)

        if not coin_id:
            await update.message.reply_text("❌ Invalid symbol")
            return

        price = await fetch_price(coin_id)

        await update.message.reply_text(
            f"{symbol.upper()} = ${price}"
        )

    except:
        await update.message.reply_text("Usage: /price BTC")