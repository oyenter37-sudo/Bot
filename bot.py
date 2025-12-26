# =====================================
# 🦔 ГОВОРЯЩИЙ ЕЖ - TELEGRAM BOT v3.0 🦔
# =====================================
# ЧАСТЬ 1/4: Импорты, настройки, БД, утилиты

import asyncio
import os
import random
from datetime import datetime, timedelta

import aiosqlite
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ChatMemberStatus

# =====================================
# ⚙️ НАСТРОЙКИ - ТОКЕН ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ
# =====================================

# Получаем токен из переменной окружения (Bothost передает BOT_TOKEN)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения. Убедитесь, что токен указан при создании бота на платформе.")

MAIN_ADMIN_USERNAME = "venter8"
CHANNEL_ID = -1002483918
CHANNEL_LINK = "https://t.me/+hGOqFr0HoQM3Mjgy"
DB_NAME = "hedgehog_bot.db"

# =====================================
# 🎨 ЦВЕТА ИГОЛОК
# =====================================

COLORS = {
    "black": "⚫ Чёрный",
    "brown": "🟤 Коричневый", 
    "white": "⚪ Белый",
    "orange": "🟠 Оранжевый",
    "gold": "🟡 Золотой",
    "blue": "🔵 Синий",
    "purple": "🟣 Фиолетовый",
    "red": "🔴 Красный",
    "green": "🟢 Зелёный",
    "rainbow": "🌈 Радужный"
}

# =====================================
# 🎰 НАСТРОЙКИ КАЗИНО
# =====================================

CASINO_EMOJI = ["🦔", "🌟", "🙀", "🎰", "👬", "🛒", "🏅", "😁"]

EJINO_MULTIPLIERS = [
    (0, 18),
    (0.5, 18),
    (1, 18),
    (1.5, 18),
    (2, 20),
    (5, 8)
]

# =====================================
# 🛒 ТОВАРЫ МАГАЗИНА
# =====================================

DEFAULT_SHOP_ITEMS = [
    ("Тухлое яблоко", 5),
    ("Яблоко", 15),
    ("Цветок", 30),
    ("Стул", 32),
    ("Стол", 35),
    ("Кусок двери", 5),
    ("Дверь", 20),
    ("Тухлый порванный зелёный матрас с мусорки", 0),
    ("Хорошая кровать", 40),
    ("Кровать", 30),
    ("Телевизовизор", 50),
    ("Телетелевизовизовизор", 70),
    ("ТВ", 100),
    ("Лампочки в пакете", 110),
    ("Часы из меди", 140),
    ("Мягкий ёж", 200),
    ("Серебряная книга", 400),
    ("Дом", 550),
    ("Собственная ракета", 999),
    ("Мини вселенная в банке", 2000),
    ("Супер-консоль >_<", 4500),
    ("Аптечка 🩹", 50)
]

# =====================================
# 🗄️ БАЗА ДАННЫХ
# =====================================

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                player_number INTEGER UNIQUE,
                balance INTEGER DEFAULT 0,
                hedgehog_name TEXT DEFAULT '🦔Ежъ🦔',
                hedgehog_color TEXT DEFAULT 'Не выбран',
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
                double_ad_until TEXT DEFAULT NULL,
                ad_index INTEGER DEFAULT 0,
                is_injured INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                ban_reason TEXT DEFAULT NULL,
                casino_wins INTEGER DEFAULT 0,
                casino_losses INTEGER DEFAULT 0,
                total_casino_profit INTEGER DEFAULT 0
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT,
                amount INTEGER DEFAULT 0,
                timestamp TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                code TEXT PRIMARY KEY,
                reward_type TEXT,
                reward_value TEXT,
                uses_left INTEGER,
                total_uses INTEGER DEFAULT 0,
                created_by TEXT DEFAULT 'Unknown',
                created_at TEXT DEFAULT NULL
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS used_promocodes (
                user_id INTEGER,
                code TEXT,
                used_at TEXT DEFAULT NULL,
                PRIMARY KEY (user_id, code)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                username TEXT PRIMARY KEY,
                added_by TEXT,
                added_at TEXT
            )
        ''')
        
        await db.execute('''
            INSERT OR IGNORE INTO admins (username, added_by, added_at)
            VALUES (?, 'system', ?)
        ''', (MAIN_ADMIN_USERNAME, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS custom_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT UNIQUE,
                response_text TEXT,
                media_type TEXT DEFAULT NULL,
                media_file_id TEXT DEFAULT NULL,
                created_by TEXT,
                created_at TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price INTEGER
            )
        ''')
        
        for name, price in DEFAULT_SHOP_ITEMS:
            await db.execute('INSERT OR IGNORE INTO shop_items (name, price) VALUES (?, ?)', (name, price))
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id INTEGER,
                quantity INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                UNIQUE(user_id, item_id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message_text TEXT,
                media_type TEXT DEFAULT NULL,
                media_file_id TEXT DEFAULT NULL,
                ticket_type TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_username TEXT,
                action TEXT,
                target_info TEXT,
                timestamp TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        default_settings = [
            ("maintenance_mode", "0"),
            ("feed_cost", "150"),
            ("ant_catch_cost", "200"),
            ("daily_reward_min", "100"),
            ("daily_reward_max", "500"),
            ("ant_income", "10"),
            ("referral_bonus", "500"),
            ("referral_reward", "100")
        ]
        
        for key, value in default_settings:
            await db.execute('INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)', (key, value))
        
        await db.commit()

# =====================================
# 🔧 УТИЛИТЫ
# =====================================

async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT value FROM bot_settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row['value'] if row else default

async def update_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def update_username(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)", 
                        (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        await db.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
        await db.commit()

async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        user = await db.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        user_row = await user.fetchone()
        if not user_row:
            return False
        username = user_row['username']
        admin = await db.execute("SELECT * FROM admins WHERE username = ?", (username,))
        return await admin.fetchone() is not None

async def is_main_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        user = await db.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        user_row = await user.fetchone()
        if not user_row:
            return False
        username = user_row['username']
        return username == MAIN_ADMIN_USERNAME

async def check_user_banned(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        user = await db.execute("SELECT is_banned, ban_reason FROM users WHERE user_id = ?", (user_id,))
        user_row = await user.fetchone()
        if user_row and user_row['is_banned']:
            return True, user_row['ban_reason']
        return False, None

async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False

def subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL_LINK)]])

# =====================================
# 🤖 ИНИЦИАЛИЗАЦИЯ БОТА И ДИСПЕТЧЕРА
# =====================================

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# =====================================
# ⏰ ПАССИВНЫЙ ДОХОД ОТ МУРАВЬЁВ
# =====================================

async def ant_income_loop():
    """Фоновая задача для начисления дохода от муравьёв каждый час"""
    while True:
        await asyncio.sleep(3600)  # 1 час
        try:
            ant_income = int(await get_setting("ant_income", "10"))
            async with aiosqlite.connect(DB_NAME) as db:
                async with db.execute("SELECT user_id, ants FROM users WHERE ants > 0") as cursor:
                    users = await cursor.fetchall()
                count = 0
                for user_id, ants in users:
                    income = ants * ant_income
                    await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (income, user_id))
                    count += 1
                await db.commit()
                if count > 0:
                    print(f"💰 Начислен доход от муравьёв: {count} пользователям")
        except Exception as e:
            print(f"Ошибка начисления муравьёв: {e}")

# =====================================
# ⚠️ ПРИМЕЧАНИЕ
# =====================================
# Остальной код бота (обработчики команд, казино, магазин, админка и т.д.)
# должен быть добавлен из оригинального файла bot.py
# 
# Основное изменение: токен теперь читается из переменной окружения BOT_TOKEN
# вместо хардкода. Это позволяет использовать бота на платформе Bothost,
# которая автоматически передает токен через переменные окружения.
# =====================================

# =====================================
# 🚀 ЗАПУСК БОТА
# =====================================
async def main():
    await init_db()
    asyncio.create_task(ant_income_loop())
    print("=" * 50)
    print("🦔 Бот 'Говорящий Еж' v3.0 запущен!")
    print("=" * 50)
    print(f"👑 Главный админ: @{MAIN_ADMIN_USERNAME}")
    print(f"📢 Канал: {CHANNEL_LINK}")
    print("=" * 50)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

