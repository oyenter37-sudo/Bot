import sqlite3

# Подключаемся к твоей базе
db_name = "hedgehog_bot.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

print("⏳ Исправляем базу данных...")

# 1. Добавляем колонку для админов (из-за неё ошибка)
try:
    cursor.execute("ALTER TABLE admins ADD COLUMN can_edit_promos INTEGER DEFAULT 0")
    print("✅ Колонка 'can_edit_promos' добавлена в таблицу admins!")
except Exception as e:
    print(f"ℹ️ Инфо по admins: {e}")

# 2. Добавляем колонку для новой валюты (на всякий случай)
try:
    cursor.execute("ALTER TABLE users ADD COLUMN elephant_skin INTEGER DEFAULT 0")
    print("✅ Колонка 'elephant_skin' добавлена в таблицу users!")
except Exception as e:
    print(f"ℹ️ Инфо по users: {e}")

conn.commit()
conn.close()
print("🎉 Готово! Теперь запускай основного бота.")
