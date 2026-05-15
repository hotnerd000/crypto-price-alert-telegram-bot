import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from handlers import start, add, price, list_alerts, remove_alert
from db import init_db
from alert_engine import AlertEngine
import socket, time
from telegram.request import HTTPXRequest
from price_service import session
from handlers import update_alert_cmd, volatile
import traceback

# Force IPv4
def force_ipv4():
    orig_getaddrinfo = socket.getaddrinfo

    def new_getaddrinfo(*args, **kwargs):
        return [
            res for res in orig_getaddrinfo(*args, **kwargs)
            if res[0] == socket.AF_INET
        ]

    socket.getaddrinfo = new_getaddrinfo

force_ipv4()

async def post_init(app):
    # Init DB
    await init_db()

    # Start alert engine
    engine = AlertEngine(app.bot)
    asyncio.create_task(engine.run())

async def post_shutdown(app):
    if session:
        await session.close()
        print("HTTP session closed")

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        pool_timeout=30.0
    )

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .post_init(post_init) 
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("list", list_alerts))
    app.add_handler(CommandHandler("remove", remove_alert))
    app.add_handler(CommandHandler("update", update_alert_cmd))
    app.add_handler(CommandHandler("volatile", volatile))

    while True:  # run forever
        try:
            print("Bot running...")
            app.run_polling()  # <-- NO await, NO asyncio.run()
            break
        except Exception as e:
            # catch all errors including network/DNS errors
            print(f"[ERROR] Bot crashed: {e}")
            traceback.print_exc()
            print("Retrying in 300 seconds...")
            time.sleep(300)  # wait a bit before retrying

if __name__ == "__main__":
    main()