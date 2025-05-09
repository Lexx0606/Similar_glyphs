import sqlite3
import os
from tqdm import tqdm

# This file is needed to create a Russian dictionary, so all further comments are in Russian
base_path = 'brks_clean.db'
nown_elements = []


# Выделение иероглифа(словарного слова) в html тегах
def zi_finder(text):
    # формат авторов словарей
    start_index = text.find("headword")
    # перед иероглифом стоит ключевое слово headword
    if (end_index := text.find("</big><br>")) == -1:
        # а конец отмечается двумя разными тегами почему-то
        end_index = text.index("</b><br>", start_index+9, )
    zi = text[start_index+10:end_index]
    return zi


# Отделение Пиньиня и остального текста
def pinyin_separation(text, pinyin_index):
    pinyin = text[:pinyin_index]
    article = text[pinyin_index:]
    return pinyin, article


# Наполнение промежуточных переменных и одновременная их дозапись в базу
def base_filler(texts, conn):
    zi_values = []
    pinyin_values = []
    article_values = []
    for text in texts:
        # Если нашел строку с ироглифами
        if "<div id=" in text:
            zi = zi_finder(text)
            # и такое слово уже было
            # !NB это очень медленно под конец! не могу придумать ничего лучше
            if zi in nown_elements:
                continue  # пропускаем его
            else:
                zi_values.append(zi)
                nown_elements.append(zi)
        # Если строке есть словарная статья
        elif (pinyin_index := text.find("<p style=")) != -1:
            # ищем, где кончается пиньин
            pinyin, article = pinyin_separation(text, pinyin_index)
            pinyin_values.append(pinyin)
            article_values.append(article)
        # Прочие строки пропускаем
        else:
            continue
    # пишем все разом в базу
    if zi_values and pinyin_values and article_values:
        conn.executemany(
            "INSERT INTO brks (zi, pinyin, rus_articles) VALUES (?, ?, ?)",
            zip(zi_values, pinyin_values, article_values)
        )
        conn.commit()


conn = sqlite3.connect(base_path)
cursor = conn.cursor()

# Создание таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS brks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zi TEXT NOT NULL,
    pinyin TEXT,
    rus_articles TEXT,
)
''')

# Все папки с html файлами словаря
adr_list = [f"dabkrs_{i}.hdir" for i in range(1, 4)]
# Идем по файлам
for folder_path in adr_list:
    file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    for item in tqdm(file_list):
        with open(item, 'r', encoding='utf-8') as file:
            texts = file.readlines()
            base_filler(texts, conn)

conn.close()

print("База из словаря сформирована")
