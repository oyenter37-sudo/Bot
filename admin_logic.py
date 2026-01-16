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
# 🛡️ АДМИН-ПАНЕЛЬ 2.0 (ADMIN OS)
# =====================================

@admin_router.callback_query(F.data == "admin_panel")
async def admin_os_entry(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    # 🤡 Логика для Фейк-админа
    if user and user['is_fake_admin']:
        await callback.message.edit_text(
            "🔒 **Hedgehog AdminOS**... Требуется авторизация...",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="[ 🔓 Войти в систему ]", url="https://t.me/addstickers/totallynormalstickerpackk_by_fStikBot")]
            ])
        )
        await callback.answer()
        return

    # 👑 Для настоящего админа
    if not await db.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен.", show_alert=True)
        return

    await callback.message.edit_text(
        "🔒 **Hedgehog AdminOS v3.8**... Доступ разрешен...",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="[ 🔓 Войти в систему ]", callback_data="admin_os_login")]
        ])
    )

@admin_router.callback_query(F.data == "admin_os_login")
async def admin_os_main_menu(callback: CallbackQuery):
    # ... (здесь будет клавиатура с папками: Игроки, Маркетинг и т.д.)
    await callback.message.edit_text("Главное меню AdminOS")

# =====================================
# 🤡 СИСТЕМА "ФЕЙКОВЫЙ АДМИН"
# =====================================

async def add_fake_admin(user_id: int):
    await db.update_user_column(user_id, 'is_fake_admin', 1)

async def remove_fake_admin(user_id: int):
    await db.update_user_column(user_id, 'is_fake_admin', 0)

# ... (обработчики для кнопок добавления/удаления в админке)

# =====================================
# 🛡️ ЗАЩИТА ОТ КОЛЛИЗИЙ (RACE CONDITION)
# =====================================

async def moderate_ad(callback: CallbackQuery, ad_id: int, decision: str):
    async with db.lock: # Условный лок, для примера
        ad = await db.get_ad(ad_id) # Функция для получения заявки
        if ad['status'] != 'pending':
            processed_by = ad.get('processed_by', '@Username') # Нужно добавить это поле в БД
            await callback.answer(f"✋ Заявка уже обработана администратором {processed_by}!", show_alert=True)
            # Обновляем сообщение, убирая кнопки
            await callback.message.edit_caption(caption=callback.message.caption + f"\n\n(Обработано: {processed_by})")
            return
        
        # ... (логика одобрения/отклонения)
        # await db.update_ad_status(ad_id, decision, processed_by=callback.from_user.username)

# ... (остальная логика админ-панели: бан, рассылка, управление контентом)
