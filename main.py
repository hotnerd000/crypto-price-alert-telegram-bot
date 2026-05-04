import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from handlers import start, add, price, list_alerts, remove_alert
from db import init_db
from alert_engine import AlertEngine
import socket
from telegram.request import HTTPXRequest

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
        .post_init(post_init)  # <-- IMPORTANT
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("list", list_alerts))
    app.add_handler(CommandHandler("remove", remove_alert))

    print("Bot running...")
    app.run_polling()  # <-- NO await, NO asyncio.run()


if __name__ == "__main__":
    main()