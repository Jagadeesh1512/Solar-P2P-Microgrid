import aiosqlite
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "microgrid.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                seller_name TEXT NOT NULL,
                buyer_id TEXT NOT NULL,
                buyer_name TEXT NOT NULL,
                energy_kwh REAL NOT NULL,
                clearing_price_usd REAL NOT NULL,
                total_cost_usd REAL NOT NULL,
                buyer_savings_usd REAL NOT NULL,
                seller_extra_profit_usd REAL NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                simulated_time TEXT NOT NULL,
                total_gen_kw REAL NOT NULL,
                total_load_kw REAL NOT NULL,
                net_power_kw REAL NOT NULL,
                grid_import_kw REAL NOT NULL,
                grid_export_kw REAL NOT NULL,
                co2_offset_kg REAL NOT NULL
            )
        """)
        await db.commit()

async def record_trade(trade_data: Dict[str, Any]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO trades (
                timestamp, seller_id, seller_name, buyer_id, buyer_name,
                energy_kwh, clearing_price_usd, total_cost_usd,
                buyer_savings_usd, seller_extra_profit_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data["timestamp"],
            trade_data["seller_id"],
            trade_data["seller_name"],
            trade_data["buyer_id"],
            trade_data["buyer_name"],
            trade_data["energy_kwh"],
            trade_data["clearing_price_usd"],
            trade_data["total_cost_usd"],
            trade_data["buyer_savings_usd"],
            trade_data["seller_extra_profit_usd"]
        ))
        await db.commit()

async def get_recent_trades(limit: int = 50) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
