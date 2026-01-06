import sqlite3

# Имя твоего файла базы данных
DB_NAME = "hedgehog_bot.db"

def fix_database():
    print(f"🔧 Начинаю лечение базы данных {DB_NAME}...")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Ошибка подключения к базе. Проверь, лежит ли этот файл рядом с {DB_NAME}")
        print(f"Ошибка: {e}")
        return

    # Список того, что нужно добавить
    updates = [
        # Таблица, Колонка, Тип данных
        ("admins", "can_edit_promos", "INTEGER DEFAULT 0"),
        ("users", "elephant_skin", "INTEGER DEFAULT 0"),
        ("shop_items", "currency", "TEXT DEFAULT 'balance'"),
        ("users", "player_number", "INTEGER"),
        ("promocodes", "created_by", "TEXT DEFAULT 'Unknown'"),
        ("promocodes", "created_at", "TEXT")
    ]

    for table, column, col_type in updates:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            print(f"✅ Успешно добавлена колонка '{column}' в таблицу '{table}'")
        except sqlite3.OperationalError as e:
            # Если колонка уже есть, sqlite вернет ошибку - это нормально, просто пропускаем
            if "duplicate column" in str(e).lower() or "no such table" in str(e).lower():
                print(f"ℹ️ Колонка '{column}' уже существует или таблицы нет (нормально).")
            else:
                print(f"⚠️ Пропуск '{column}' в '{table}': {e}")

    # Создаем новую таблицу для медиа, если её нет
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screen_media (
                screen_name TEXT PRIMARY KEY,
                file_id TEXT,
                media_type TEXT
            )
        ''')
        print("✅ Таблица 'screen_media' проверена/создана")
    except Exception as e:
        print(f"❌ Ошибка создания screen_media: {e}")

    conn.commit()
    conn.close()
    print("\n🎉 ЛЕЧЕНИЕ ЗАВЕРШЕНО! Теперь запускай основного бота.")

if __name__ == "__main__":
    fix_database()
