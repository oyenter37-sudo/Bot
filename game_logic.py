# =====================================
# 🦔 HEDGEHOG BOT v3.8 - GAME LOGIC 🦔
# =====================================

import random
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

import database as db
from config import (
    CLASSES, FOOD_ITEMS, DIAMOND_EXCHANGE_RATE, 
    UserStates, AdminStates
)

game_router = Router()

# =====================================
# 🖥️ ГЛАВНОЕ МЕНЮ И ЗАГЛУШКИ
# =====================================

def get_main_menu_keyboard():
    """Собирает новую клавиатуру главного меню v3.8."""
    buttons = [
        [ # 1-й ряд
            InlineKeyboardButton(text="Покормить", callback_data="feed"),
            InlineKeyboardButton(text="Погладить", callback_data="pet")
        ],
        [ # 2-й ряд
            InlineKeyboardButton(text="Магазин", callback_data="shop"),
            InlineKeyboardButton(text="⚒️ Кузница", callback_data="placeholder_forge")
        ],
        [ # 3-й ряд
            InlineKeyboardButton(text="💎 Алмазы", callback_data="diamonds_menu"),
            InlineKeyboardButton(text="🤖 ИИ-ЕЖ", callback_data="placeholder_ai_hedgehog")
        ],
        [ # 4-й ряд и далее - остальные кнопки
            InlineKeyboardButton(text="Перевод", callback_data="transfer_menu"),
            InlineKeyboardButton(text="Сайт", url="https://t.me/SpeakingHedgehog") # Пример ссылки
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@game_router.callback_query(F.data.in_(["placeholder_forge", "placeholder_ai_hedgehog"]))
async def placeholder_callback(callback: CallbackQuery):
    """Обрабатывает нажатия на кнопки-заглушки."""
    await callback.answer(
        "🚧 Раздел в разработке\nЭтот функционал появится в ближайших обновлениях. Следите за новостями!",
        show_alert=True
    )

# =====================================
# 💎 НОВАЯ ЭКОНОМИКА (АЛМАЗЫ)
# =====================================

@game_router.callback_query(F.data == "diamonds_menu")
async def diamonds_menu(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    text = (
        f"💎 **Алмазное Меню** 💎\n\n"
        f"Ваш баланс: {user['diamonds']} алмазов 💎\n"
        f"Кожа слона: {user['elephant_skin']} 🐘\n\n"
        f"Здесь вы можете обменять Кожу слона на Алмазы и наоборот, а также приобрести уникальные VIP-товары."
    )
    buttons = [
        [InlineKeyboardButton(text=f"💎 1 <-> 🐘 {DIAMOND_EXCHANGE_RATE}", callback_data="exchange_diamonds_menu")],
        [InlineKeyboardButton(text="🏆 Топ по Алмазам", callback_data="top_diamonds")],
        [InlineKeyboardButton(text="💎 VIP-товары", callback_data="vip_shop")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

async def secret_diamond_drop(message: Message, user_id: int):
    """С шансом 1% даёт алмаз при кормлении или поглаживании."""
    if random.random() <= 0.01:
        await db.update_user_balance(user_id, diamond_change=1)
        await message.answer("КХЕ-КХЕ... Ёж подавился и выплюнул АЛМАЗ! 💎")

# =====================================
# ⚖️ РЕБАЛАНС КАЗИНО (ИГРА "ЗВЕЗДЫ")
# =====================================

@game_router.callback_query(F.data.startswith("star_reveal_"))
async def star_game_reveal(callback: CallbackQuery, state: FSMContext):
    # ... (код получения state data)
    user_id = callback.from_user.id
    data = await state.get_data()
    bet = data['bet']

    # Списываем ставку
    await db.update_user_balance(user_id, balance_change=-bet)

    # ... (логика определения, звезда или нет)
    is_star = True # условно

    if is_star:
        win = int(bet * 2.5)
        await db.update_user_balance(user_id, balance_change=win)
        await callback.answer(f"🌟 ЗВЕЗДА! +{win}", show_alert=True)
    else:
        # Просто списали ставку, ничего не возвращаем (x0 множитель)
        await callback.answer(f"❌ Пусто! Ставка сгорела.", show_alert=True)
    
    # ... (обновление сообщения с полем)

# =====================================
# ☠️ МЕХАНИКА ВЫЖИВАНИЯ (ПОСМЕРТИЕ)
# =====================================

def get_death_menu_keyboard():
    """Клавиатура для мертвого ежа (без рекламы)."""
    buttons = [
        [InlineKeyboardButton(text="Кликер (+1💰)", callback_data="death_clicker")],
        [InlineKeyboardButton(text="Попрошайничать", callback_data="death_beg")],
        [InlineKeyboardButton(text="Купить нового ежа", callback_data="buy_new_hedgehog")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# При проверке доступа к функциям, если ёж мёртв, вместо блокировки 
# нужно отправлять сообщение с этой клавиатурой.

# ... (остальная игровая логика: кормление, погладить, магазин и т.д., адаптированная под новые функции)
