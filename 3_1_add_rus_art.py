import sqlite3
from tqdm import tqdm
import re
embedding_base = 'zi.db'
dikt_base = 'brks.db'


# удаляем нежуные признаки классов из исходного словаря
def style_cleaner(line):
    cleaned_line = re.sub(r'<span class="sec">|<span class="ex">|</span>', '', line)
    return cleaned_line


# удаляем примеры
def example_cleaner(content):
    pattern = r'<p style="padding-left:([2-5])em;margin:0"><font color="steelblue.*?</p>'
    replacement = ''
    # Заменяем найденные участки на пустую строку
    cleaned_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return cleaned_content


# Открытие таблиц
conn_files = sqlite3.connect(embedding_base)
cursor_files = conn_files.cursor()

conn_brks = sqlite3.connect(dikt_base)
cursor_brks = conn_brks.cursor()

# Получение значений из таблицы files
cursor_files.execute("SELECT zi FROM files")
zi_values = cursor_files.fetchall()

# Проход по каждому значению из таблицы files
for zi in tqdm(zi_values):
    zi_value = zi[0]  # Получаем zi
    # Запрос для получения значений из таблицы brks
    query = "SELECT pinyin, rus_articles FROM brks WHERE zi = ?"
    cursor_brks.execute(query, (zi_value,))
    # Получение результатов запроса
    result = cursor_brks.fetchone()
    if result:
        # выдялем пиньин и статью
        pinyin, rus_articles = result
        ru_full_art = style_cleaner(rus_articles)
        # статья без примеров - короткая
        ru_short_art = example_cleaner(ru_full_art)
        # Обновление строки в таблице files
        update_query = "UPDATE files SET pinyin = ?, ru_short_art = ?, ru_full_art = ? WHERE zi = ?"
        cursor_files.execute(update_query, (pinyin, ru_short_art, ru_full_art, zi_value))
        # Сохранение изменений в таблице files
        conn_files.commit()
# Закрытие соединений
cursor_files.close()
conn_files.close()
cursor_brks.close()
conn_brks.close()
