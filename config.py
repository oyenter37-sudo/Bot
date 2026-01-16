# =====================================
# 🦔 HEDGEHOG BOT v3.8 - CONFIG 🦔
# =====================================

from aiogram.fsm.state import State, StatesGroup

# =====================================
# ⚙️ ГЛАВНЫЕ НАСТРОЙКИ
# =====================================

BOT_TOKEN = "7230762282:AAFUR5TOhC4dK-i7QPz3PyHzYYVycwSc85g" # ВАШ ТОКЕН
MAIN_ADMIN_USERNAME = "venter8" # @username главного админа
CHANNEL_ID = -1002483918 # ID канала для подписки
CHANNEL_LINK = "https://t.me/+hGOqFr0HoQM3Mjgy" # Ссылка на канал
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
# 🤠 КЛАССЫ ЕЖЕЙ
# =====================================

CLASSES = {
    "normal": {"name": "Обычный Еж 🦔", "price": 220, "max_satiety": 100},
    "ejidze": {"name": "Ежидзе 🤠", "price": 350, "max_satiety": 100},
    "fat": {"name": "Толстый Еж 🦔", "price": 300, "max_satiety": 200},
    "golden": {"name": "Золотой Еж 🟡", "price": 600, "max_satiety": 100}
}

# =====================================
# 🥕 ЕДА
# =====================================

FOOD_ITEMS = [
    ("Тухлое яблоко", 2, 1),
    ("Яблоко", 5, 4),
    ("Груша", 6, 5),
    ("Жук-хрущ", 12, 10),
    ("Молоко кота", 30, 20),
    ("Молоко", 39, 25),
    ("Хлеб", 59, 40),
    ("Капуста", 70, 50),
    ("Электрический робот насыщитель", 111, 100)
]

# =====================================
# 💎 ЭКОНОМИКА АЛМАЗОВ
# =====================================

DIAMOND_EXCHANGE_RATE = 3 # 3 кожи слона за 1 алмаз

# =====================================
# 📜 ЛИМИТЫ
# =====================================

INVENTORY_STACK_LIMIT = 100 # Макс. кол-во одного предмета в инвентаре

# =====================================
# 📋 FSM СОСТОЯНИЯ
# =====================================

class UserStates(StatesGroup):
    waiting_name = State()
    waiting_ad_photo = State()
    waiting_support_message = State()
    waiting_suggestion_message = State()
    casino_bet = State()
    dice_numbers = State()
    star_game = State()
    image_test_text = State()
    transfer_user = State()
    transfer_amount = State()
    custom_bet_amount = State()
    # Books FSM
    book_title = State()
    book_text = State()
    book_price = State()
    # Diamonds FSM
    exchange_diamonds = State()

class AdminStates(StatesGroup):
    # Main Admin Panel
    waiting_user_search = State()
    waiting_ban_reason = State()
    waiting_personal_message = State()
    # Marketing
    waiting_broadcast_message = State()
    waiting_promo_code = State()
    waiting_promo_type = State()
    waiting_promo_value = State()
    waiting_promo_uses = State()
    # Content
    waiting_item_name = State()
    waiting_item_price = State()
    waiting_item_currency = State()
    waiting_command_name = State()
    waiting_command_response = State()
    waiting_add_screen_name = State()
    waiting_add_media = State()
    # Settings
    waiting_setting_value = State()
    waiting_admin_username = State()
    # Fake Admins
    waiting_fake_admin_id = State()
