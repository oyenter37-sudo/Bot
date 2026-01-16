# =====================================
# 🦔 HEDGEHOG BOT v3.8 - DATABASE 🦔
# =====================================

import aiosqlite
from datetime import datetime
import asyncio

# Используем относительные импорты, так как это теперь модуль
from config import DB_NAME, MAIN_ADMIN_USERNAME, INVENTORY_STACK_LIMIT

# Блокировка для предотвращения состояния гонки при модерации
db_lock = asyncio.Lock()

# =====================================
# 🗄️ ИНИЦИАЛИЗАЦИЯ И МИГРАЦИЯ
# =====================================

async def init_db():
    """Инициализирует базу данных, создает таблицы и выполняет миграцию."""
    async with aiosqlite.connect(DB_NAME) as db:
        # --- USERS TABLE ---
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                player_number INTEGER UNIQUE,
                balance INTEGER DEFAULT 0,
                elephant_skin INTEGER DEFAULT 0,
                diamonds INTEGER DEFAULT 0,
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
                ban_ads INTEGER DEFAULT 0,
                ban_books INTEGER DEFAULT 0,
                is_fake_admin INTEGER DEFAULT 0,
                alert_sent INTEGER DEFAULT 0,
                casino_wins INTEGER DEFAULT 0,
                casino_losses INTEGER DEFAULT 0,
                total_casino_profit INTEGER DEFAULT 0
            )
        ''')

        # --- OTHER TABLES ---
        await db.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                action_type TEXT, amount INTEGER DEFAULT 0, timestamp TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                code TEXT PRIMARY KEY, reward_type TEXT, reward_value TEXT,
                uses_left INTEGER, total_uses INTEGER DEFAULT 0, created_by TEXT, created_at TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS used_promocodes (
                user_id INTEGER, code TEXT, used_at TEXT, PRIMARY KEY (user_id, code)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, file_id TEXT,
                status TEXT DEFAULT 'pending', created_at TEXT,
                moderator_username TEXT DEFAULT NULL -- v3.8 for race condition
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                username TEXT PRIMARY KEY, added_by TEXT, added_at TEXT, can_edit_promos INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price INTEGER,
                currency TEXT DEFAULT 'balance', category TEXT DEFAULT 'other' -- v3.8 for furniture
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id INTEGER,
                quantity INTEGER DEFAULT 0, UNIQUE(user_id, item_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, author_username TEXT,
                title TEXT, content TEXT, price INTEGER, status TEXT DEFAULT 'pending',
                created_at TEXT, moderator_username TEXT DEFAULT NULL -- v3.8 for race condition
            )
        ''')

        # --- МИГРАЦИЯ СТАРЫХ И НОВЫХ КОЛОНОК ---
        all_columns = {
            "users": [
                ("diamonds", "INTEGER DEFAULT 0"),
                ("ban_ads", "INTEGER DEFAULT 0"),
                ("ban_books", "INTEGER DEFAULT 0"),
                ("is_fake_admin", "INTEGER DEFAULT 0"),
                ("alert_sent", "INTEGER DEFAULT 0"),
                # Колонки из старых версий для обратной совместимости
                ("player_number", "INTEGER"), ("is_injured", "INTEGER DEFAULT 0"),
                ("is_banned", "INTEGER DEFAULT 0"), ("ban_reason", "TEXT"),
                ("casino_wins", "INTEGER DEFAULT 0"), ("casino_losses", "INTEGER DEFAULT 0"),
                ("total_casino_profit", "INTEGER DEFAULT 0"), ("elephant_skin", "INTEGER DEFAULT 0"),
                ("hedgehog_class", "TEXT DEFAULT 'normal'"), ("status", "TEXT DEFAULT 'alive'"),
                ("satiety", "REAL DEFAULT 100.0"), ("last_beg", "TEXT DEFAULT NULL")
            ],
            "promocodes": [("created_by", "TEXT DEFAULT 'Unknown'"), ("created_at", "TEXT")],
            "shop_items": [("currency", "TEXT DEFAULT 'balance'"), ("category", "TEXT DEFAULT 'other'")],
            "admins": [("can_edit_promos", "INTEGER DEFAULT 0")],
            "ads": [("moderator_username", "TEXT DEFAULT NULL")],
            "books": [("moderator_username", "TEXT DEFAULT NULL")]
        }

        for table, columns in all_columns.items():
            for column, col_type in columns:
                try:
                    await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                except aiosqlite.OperationalError:
                    pass  # Колонка уже существует

        await db.commit()

        # --- Первичная настройка ---
        await db.execute("INSERT OR IGNORE INTO admins (username, added_by, added_at, can_edit_promos) VALUES (?, 'system', ?, 1)",
                         (MAIN_ADMIN_USERNAME, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # Обновление категории для мебели
        furniture_items = ["Стул", "Стол", "Кровать", "Хорошая кровать", "Диван"] # Пример
        for item_name in furniture_items:
             await db.execute("UPDATE shop_items SET category = 'Мебель' WHERE name = ?", (item_name,))

        await db.commit()
    print("✅ База данных инициализирована и мигрирована для v3.8!")


# =====================================
# 🔧 ОБЕРТКИ-УТИЛИТЫ ДЛЯ БД
# =====================================

async def _execute_query(query, params=(), fetch=None):
    """Универсальная функция для выполнения запросов."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            if fetch == "one":
                return await cursor.fetchone()
            if fetch == "all":
                return await cursor.fetchall()
            await db.commit()

async def get_user(user_id: int):
    return await _execute_query("SELECT * FROM users WHERE user_id = ?", (user_id,), fetch="one")

async def update_user_column(user_id: int, column: str, value):
    return await _execute_query(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))

async def update_user_balance(user_id: int, balance_change: int = 0, skin_change: int = 0, diamond_change: int = 0):
    await _execute_query("UPDATE users SET balance = balance + ?, elephant_skin = elephant_skin + ?, diamonds = diamonds + ? WHERE user_id = ?",
                         (balance_change, skin_change, diamond_change, user_id))

async def get_all_user_ids(only_alive: bool = False):
    sql = "SELECT user_id FROM users" + (" WHERE status = 'alive'" if only_alive else "")
    rows = await _execute_query(sql, fetch="all")
    return [row['user_id'] for row in rows]

async def is_admin(user_id: int) -> bool:
    user = await get_user(user_id)
    if not (user and user['username']):
        return False
    admin_record = await _execute_query("SELECT * FROM admins WHERE username = ?", (user['username'],), fetch="one")
    return admin_record is not None

async def is_fake_admin(user_id: int) -> bool:
    user = await get_user(user_id)
    return user and user['is_fake_admin'] == 1

async def get_users_with_item_category(category: str):
    """Возвращает ID пользователей, у которых есть предмет указанной категории."""
    rows = await _execute_query('''
        SELECT DISTINCT i.user_id FROM inventory i
        JOIN shop_items s ON i.item_id = s.id
        WHERE s.category = ? AND i.quantity > 0
    ''', (category,), fetch="all")
    return [row['user_id'] for row in rows]

async def add_inventory_item(user_id: int, item_id: int, quantity: int = 1):
    """Добавляет предмет в инвентарь, учитывая лимит."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id)) as cursor:
            current_row = await cursor.fetchone()
        current_quantity = current_row[0] if current_row else 0

        if current_quantity + quantity > INVENTORY_STACK_LIMIT:
            return False  # Превышен лимит

        await db.execute('''
            INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?
        ''', (user_id, item_id, quantity, quantity))
        await db.commit()
    return True

async def get_ad_for_moderation(ad_id: int):
    return await _execute_query("SELECT * FROM ads WHERE id = ?", (ad_id,), fetch="one")

async def update_ad_status(ad_id: int, status: str, moderator: str):
    return await _execute_query("UPDATE ads SET status = ?, moderator_username = ? WHERE id = ? AND status = 'pending'", (status, moderator, ad_id))

async def get_book_for_moderation(book_id: int):
    return await _execute_query("SELECT * FROM books WHERE id = ?", (book_id,), fetch="one")

async def update_book_status(book_id: int, status: str, moderator: str):
     return await _execute_query("UPDATE books SET status = ?, moderator_username = ? WHERE id = ? AND status = 'pending'", (status, moderator, book_id))

async def create_user(user_id: int, username: str, referrer_id: int = None):
    # ... (логика создания пользователя из старого файла)
    pass
