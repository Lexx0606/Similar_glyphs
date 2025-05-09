import sqlite3
from tqdm import tqdm
import re


# remove the slashes at the edges, and replace them with a semicolon in the middle
def art_clean(leftover):
    leftover = leftover.lstrip('')
    leftover = leftover.lstrip('/')
    leftover = leftover.rstrip('')
    leftover = leftover.rstrip('/')
    leftover = leftover.replace('/', ';')
    return leftover


# https://github.com/ProxPxD/Hanzi_searcher/blob/master/cedict_ts.u8
file_name = 'dictionaries/cedict_ts.u8'
db_name = 'eng_dict.db'

conn = sqlite3.connect(db_name)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS eng_dict (
    zi TEXT,
    old_zi TEXT,
    pinyin TEXT,
    eng_art TEXT
)
''')
# variables that would insert multiple values into the database at once
zi_s = []
old_zi_s = []
pinyin_s = []
eng_art_s = []

# read the file line by line
with open(file_name, 'r') as file:
    for line in tqdm(file):
        # separating the columns
        zi, leftover = line.split(' ', 1)
        zi_s.append(zi)
        old_zi, leftover = leftover.split(' ', 1)
        old_zi_s.append(old_zi)
        match = re.search(r'\[([^]]+)\]', leftover)
        if match:
            pinyin = match.group(1)
            # deleting found content from a line
            leftover = re.sub(r'\[([^]]+)\]', '', leftover)
            pinyin_s.append(pinyin)
        # cleaning the article
        eng_art = art_clean(leftover)
        eng_art_s.append(eng_art)
    # recording everything in the database in one step
    if zi_s and old_zi_s and pinyin_s and eng_art_s:
        conn.executemany(
            "INSERT INTO eng_dict (zi, old_zi, pinyin, eng_art) VALUES (?, ?, ?, ?)",
            zip(zi_s, old_zi_s, pinyin_s, eng_art_s)
        )
conn.commit()
conn.close()

print("The data has been successfully uploaded to the database.")
