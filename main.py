# =====================================
# 🦔 HEDGEHOG BOT v3.8 - MAIN 🦔
# =====================================

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from config import BOT_TOKEN, MAIN_ADMIN_USERNAME, CLASSES
from game_logic import game_router # Предполагается, что роутер будет создан в game_logic
from admin_logic import admin_router

# =====================================
# ⏰ ФОНОВЫЕ ЗАДАЧИ (LOOPS)
# =====================================

async def hunger_loop(bot: Bot):
    while True:
        await asyncio.sleep(600) # Каждые 10 минут
        try:
            all_users = await db.get_all_user_ids(only_alive=True)
            if not all_users:
                continue

            # Определяем, у кого есть мебель для снижения голода
            # (Это упрощенная логика, в реальности нужен JOIN с инвентарем)
            users_with_furniture = await db.get_users_with_item_category("Мебель") # Новая функция в db

            for user_id in all_users:
                user = await db.get_user(user_id)
                if not user or user['status'] != 'alive':
                    continue

                # Математика голода
                hunger_rate = 0.15 if user_id in users_with_furniture else 0.23
                new_satiety = max(0, user['satiety'] - hunger_rate)

                await db.update_user_column(user_id, 'satiety', new_satiety)

                # Проверка на смерть
                if new_satiety <= 0:
                    await db.update_user_column(user_id, 'status', 'dead')
                    try:
                        # ... (отправка сообщения о смерти)
                        pass
                    except Exception:
                        pass
                    continue # Пропускаем уведомление о голоде, если уже умер

                # Уведомление о голоде
                if new_satiety <= 20 and user['alert_sent'] == 0:
                    try:
                        await bot.send_message(user_id, "🆘 ХОЗЯИН! Я ГОЛОДЕН! Моя сытость упала до 20%!...")
                        await db.update_user_column(user_id, 'alert_sent', 1)
                    except Exception:
                        pass

        except Exception as e:
            print(f"[ERROR in hunger_loop]: {e}")

# =====================================
# 🚀 ЗАПУСК БОТА
# =====================================
async def main():
    # Инициализация
    await db.init_db()
    
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров
    dp.include_router(admin_router)
    dp.include_router(game_router)
    # ... (здесь же будут основные хендлеры, типа /start)
    
    # Запуск фоновых задач
    asyncio.create_task(hunger_loop(bot))
    # asyncio.create_task(ant_income_loop()) # ... и другие

    print("Hedgehog Bot v3.8 (Survival Update) запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
