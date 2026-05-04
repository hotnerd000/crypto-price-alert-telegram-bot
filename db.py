import aiosqlite

DB_NAME = "alerts.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symbol TEXT,
    coin_id TEXT,
    tp REAL,
    sl REAL,
    interval INTEGER,
    last_checked INTEGER,
    triggered INTEGER DEFAULT 0
);
"""

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(CREATE_TABLE)
        await db.commit()

async def add_alert(user_id, symbol, coin_id, tp, sl, interval):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO alerts (user_id, symbol, coin_id, tp, sl, interval, last_checked)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (user_id, symbol, coin_id, tp, sl, interval))
        await db.commit()

async def get_alerts():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM alerts")
        return await cursor.fetchall()

async def update_last_checked(alert_id, ts):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE alerts SET last_checked=? WHERE id=?",
            (ts, alert_id)
        )
        await db.commit()

async def mark_triggered(alert_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE alerts SET triggered=1 WHERE id=?",
            (alert_id,)
        )
        await db.commit()