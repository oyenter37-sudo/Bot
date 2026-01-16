# =====================================
# 🦔 HEDGEHOG BOT v3.8 - ADMIN LOGIC 🦔
# =====================================

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

import database as db
from config import AdminStates

admin_router = Router()

# =====================================
# 🤡 СИСТЕМА "ФЕЙКОВЫЙ АДМИН"
# =====================================

async def show_admin_reply_keyboard(user_id: int):
    """Возвращает Reply-клавиатуру, только если юзер - админ или фейк-админ."""
    is_true_admin = await db.is_admin(user_id)
    is_fake = await db.is_fake_admin(user_id)

    if is_true_admin or is_fake:
        return InlineKeyboardMarkup(inline_keyboard=[
            [KeyboardButton(text="🛠 Панель")]
        ])
    return None # Для обычных юзеров

@admin_router.message(F.text == "🛠 Панель")
async def handle_panel_button(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    # 🤡 Фейковый админ
    if await db.is_fake_admin(user_id):
        await message.answer(
            "🔒 **Hedgehog AdminOS**... Требуется авторизация...",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="[ 🔓 Войти в систему ]", url="https://t.me/addstickers/totallynormalstickerpackk_by_fStikBot")]
            ])
        )
        return

    # 👑 Настоящий админ
    if await db.is_admin(user_id):
        await message.answer(
            "🔒 **Hedgehog AdminOS v3.8**... Доступ разрешен...",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="[ 🔓 Войти в систему ]", callback_data="admin_os_login")]
            ])
        )
    # Обычные пользователи эту кнопку не увидят, но на всякий случай


@admin_router.callback_query(F.data == "admin_os_login")
async def admin_os_main_menu(callback: CallbackQuery):
    # Создаем "папки" админ-панели
    buttons = [
        [InlineKeyboardButton(text="👥 Игроки", callback_data="admin_folder_players")],
        [InlineKeyboardButton(text="📢 Маркетинг", callback_data="admin_folder_marketing")],
        [InlineKeyboardButton(text="🛒 Контент", callback_data="admin_folder_content")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_folder_settings")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")] # Статистика - отдельный экран
    ]
    await callback.message.edit_text("🗄️ **AdminOS** / Главная", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================
# FOLDER: Игроки
# =====================================
@admin_router.callback_query(F.data == "admin_folder_players")
async def admin_folder_players(callback: CallbackQuery):
    buttons = [
        [InlineKeyboardButton(text="🔍 Поиск / Бан", callback_data="admin_player_search")],
        [InlineKeyboardButton(text="👻 Управление Фейк-Админами", callback_data="admin_fake_admin_menu")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_os_login")]
    ]
    await callback.message.edit_text("🗄️ **AdminOS** / 👥 Игроки", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@admin_router.callback_query(F.data == "admin_fake_admin_menu")
async def fake_admin_menu(callback: CallbackQuery):
    # ... (кнопки "Добавить фейка", "Удалить фейка")
    pass

# =====================================
# 🛡️ ЗАЩИТА ОТ КОЛЛИЗИЙ (RACE CONDITION)
# =====================================

async def approve_ad(callback: CallbackQuery, ad_id: int):
    moderator_username = callback.from_user.username
    async with db.db_lock:
        ad = await db.get_ad_for_moderation(ad_id)
        if ad['status'] != 'pending':
            await callback.answer(f"✋ Заявка уже обработана администратором @{ad['moderator_username']}!", show_alert=True)
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n(Обработано @{ad['moderator_username']})", reply_markup=None)
            return
        
        # Обновляем статус с указанием модератора
        await db.update_ad_status(ad_id, 'approved', moderator_username)
        # ... (отправка уведомления юзеру)
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n✅ Одобрено вами", reply_markup=None)
    await callback.answer("✅ Реклама одобрена!")

# ... (аналогичная логика для reject_ad, approve_book, reject_book)

# ... (здесь будет остальная логика админки: рассылки, промокоды, контент и т.д., разбитая по папкам)
