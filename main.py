import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from handlers import start, add, price
from db import init_db
from alert_engine import AlertEngine

async def main():
    await init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("price", price))

    engine = AlertEngine(app.bot)

    asyncio.create_task(engine.run())

    print("Bot running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())