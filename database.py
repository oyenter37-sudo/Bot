# =====================================
# 🦔 HEDGEHOG BOT v3.8 - DATABASE 🦔
# =====================================

import aiosqlite
from datetime import datetime

from config import DB_NAME, MAIN_ADMIN_USERNAME, INVENTORY_STACK_LIMIT

# =====================================
# 🗄️ ИНИЦИАЛИЗАЦИЯ И МИГРАЦИЯ
# =====================================

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # 1. USERS TABLE
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                player_number INTEGER UNIQUE,
                balance INTEGER DEFAULT 0,
                elephant_skin INTEGER DEFAULT 0,
                diamonds INTEGER DEFAULT 0, -- v3.8
                hedgehog_name TEXT DEFAULT '🦔Ежъ🦔',
                hedgehog_color TEXT DEFAULT 'Не выбран',
                hedgehog_class TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'alive',
                satiety REAL DEFAULT 100.0,
                happiness REAL DEFAULT 0,
                ants INTEGER DEFAULT 0,
                ant_chance REAL DEFAULT 10.0,
                referrer_id INTEGER DEFAULT NULL,
                referrals_count INTEGER DEFAULT 0,
                referrals_earned INTEGER DEFAULT 0,
                total_feedings INTEGER DEFAULT 0,
                join_date TEXT,
                last_daily TEXT DEFAULT NULL,
                last_ant_collect TEXT DEFAULT NULL,
                last_beg TEXT DEFAULT NULL,
                double_ad_until TEXT DEFAULT NULL,
                ad_index INTEGER DEFAULT 0,
                is_injured INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                ban_reason TEXT DEFAULT NULL,
                ban_ads INTEGER DEFAULT 0, -- v3.8
                ban_books INTEGER DEFAULT 0, -- v3.8
                is_fake_admin INTEGER DEFAULT 0, -- v3.8
                alert_sent INTEGER DEFAULT 0, -- v3.8
                casino_wins INTEGER DEFAULT 0,
                casino_losses INTEGER DEFAULT 0,
                total_casino_profit INTEGER DEFAULT 0
            )
        ''')

        # 2. OTHER TABLES (EXISTING)
        await db.execute('''CREATE TABLE IF NOT EXISTS stats (...) ''') # ... (rest of the tables are the same)
        # ... (imagine all other CREATE TABLE statements from the old file are here)

        # 3. МИГРАЦИЯ (ДОБАВЛЕНИЕ НОВЫХ КОЛОНОК v3.8)
        new_columns = [
            ("users", "diamonds", "INTEGER DEFAULT 0"),
            ("users", "ban_ads", "INTEGER DEFAULT 0"),
            ("users", "ban_books", "INTEGER DEFAULT 0"),
            ("users", "is_fake_admin", "INTEGER DEFAULT 0"),
            ("users", "alert_sent", "INTEGER DEFAULT 0")
        ]

        for table, column, col_type in new_columns:
            try:
                await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                print(f"Migrated: Added column '{column}' to table '{table}'.")
            except aiosqlite.OperationalError as e:
                if "duplicate column name" in str(e):
                    pass # Колонка уже существует
                else:
                    raise e

        await db.commit()
        print("✅ База данных инициализирована и мигрирована для v3.8!")

# =====================================
# 🔧 ОБЕРТКИ ДЛЯ SQL-ЗАПРОСОВ
# =====================================

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_column(user_id: int, column: str, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

async def get_all_user_ids(only_alive: bool = False):
    query = "SELECT user_id FROM users"
    if only_alive:
        query += " WHERE status = 'alive'"
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(query) as cursor:
            return [u[0] for u in await cursor.fetchall()]

async def find_user_flexible(search_input: str):
    # ... (same as before)
    pass

async def get_setting(key: str, default: str = "0") -> str:
    # ... (same as before)
    pass

async def set_setting(key: str, value: str):
    # ... (same as before)
    pass

async def add_inventory_item(user_id: int, item_id: int, quantity: int = 1, price: int = 0) -> bool:
    """Добавляет предмет в инвентарь, учитывая лимит стека."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id)) as cursor:
            current_quantity_row = await cursor.fetchone()
            current_quantity = current_quantity_row[0] if current_quantity_row else 0

        if current_quantity + quantity > INVENTORY_STACK_LIMIT:
            return False # Превышен лимит

        await db.execute('''
            INSERT INTO inventory (user_id, item_id, quantity, total_spent)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET
                quantity = quantity + ?,
                total_spent = total_spent + ?
        ''', (user_id, item_id, quantity, price * quantity, quantity, price * quantity))
        await db.commit()
    return True

# ... (все остальные функции из старого файла database.py, такие как get_all_admins, add_admin_log и т.д.)
