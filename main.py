# =====================================
# 🦔 HEDGEHOG BOT v3.8 - MAIN 🦔
# =====================================

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

# Импортируем созданные модули
import database as db
from config import BOT_TOKEN, CLASSES
from game_logic import game_router, get_main_menu_keyboard, get_death_menu_keyboard, secret_diamond_drop
from admin_logic import admin_router, show_admin_reply_keyboard

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# =====================================
# ⏰ ФОНОВЫЕ ЗАДАЧИ (LOOPS)
# =====================================

async def hunger_loop(bot: Bot):
    """Основной цикл голода, смерти и уведомлений."""
    while True:
        await asyncio.sleep(600)  # Каждые 10 минут
        try:
            users_with_furniture = await db.get_users_with_item_category("Мебель")
            
            # Получаем всех живых пользователей для обработки
            alive_users = await db._execute_query("SELECT * FROM users WHERE status = 'alive'", fetch="all")

            for user in alive_users:
                user_id = user['user_id']
                hunger_rate = 0.15 if user_id in users_with_furniture else 0.23
                new_satiety = max(0, user['satiety'] - hunger_rate)

                await db.update_user_column(user_id, 'satiety', new_satiety)

                # 1. Проверка на СМЕРТЬ
                if new_satiety <= 0:
                    await db.update_user_column(user_id, 'status', 'dead')
                    try:
                        await bot.send_message(user_id, 
                                             "☠️ Ваш ёжик умер от голода...", 
                                             reply_markup=get_death_menu_keyboard())
                    except Exception as e:
                        logging.warning(f"Failed to notify user {user_id} about death: {e}")
                    continue

                # 2. Уведомление о голоде
                if new_satiety <= 20 and user['alert_sent'] == 0:
                    try:
                        await bot.send_message(user_id, "🆘 ХОЗЯИН! Я ГОЛОДЕН! Моя сытость упала до 20%! Покорми меня, иначе я умру...")
                        await db.update_user_column(user_id, 'alert_sent', 1)
                    except Exception as e:
                        logging.warning(f"Failed to send hunger alert to {user_id}: {e}")

        except Exception as e:
            logging.error(f"[ERROR in hunger_loop]: {e}")

# =====================================
# 🚀 ОБРАБОТЧИКИ START И MENU
# =====================================

@game_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"
    
    user = await db.get_user(user_id)
    if not user:
        # Логика для рефералов
        referrer_id = None
        args = message.text.split()
        if len(args) > 1:
            try: referrer_id = int(args[1])
            except (ValueError, IndexError): pass
        
        await db.create_user(user_id, username, referrer_id)
        user = await db.get_user(user_id)
    
    if user['status'] != 'alive':
        await message.answer("🪦 Вы в посмертии...", reply_markup=get_death_menu_keyboard())
    else:
        await message.answer(f"Привет, {username}!", reply_markup=await show_admin_reply_keyboard(user_id))
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())

@game_router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Главное меню:", reply_markup=get_main_menu_keyboard())

# Сброс флага голода при кормлении
@game_router.callback_query(F.data.startswith("feed_item_"))
async def process_feeding(callback: CallbackQuery):
    user_id = callback.from_user.id
    # ... (логика кормления)
    await db.update_user_column(user_id, 'alert_sent', 0) # Сброс флага
    await secret_diamond_drop(callback.message, user_id) # Шанс на алмаз
    # ... (ответ пользователю)

# =====================================
# 🚀 ЗАПУСК БОТА
# =====================================
async def main():
    # Инициализация БД
    await db.init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение роутеров
    dp.include_router(admin_router)
    dp.include_router(game_router) # game_router должен быть последним, чтобы не перехватывать команды админа
    
    # Запуск фоновых задач
    asyncio.create_task(hunger_loop(bot))
    # asyncio.create_task(other_loops...) # Можно добавить другие циклы

    logging.info("Hedgehog Bot v3.8 (Survival Update) запущен!")
    
    # Удаление вебхука перед запуском
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск полинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
