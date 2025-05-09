import sqlite3
from tqdm import tqdm

file_name = 'dictionaries/full_zi.txt'
full_zi = []
# open base
base_file = 'brks_clean.db'
conn = sqlite3.connect(base_file)
cursor = conn.cursor()
# getiing all
query = "SELECT zi FROM brks"
try:
    cursor.execute(query)
    rows = cursor.fetchall()

except sqlite3.Error as e:
    print("Ошибка при выполнении запроса:", e)

finally:
    conn.close()

# separting zi and words
for row in tqdm(rows):
    if len(row[0]) > 1:
        continue
    else:
        full_zi.append(row[0])

# writing zi
with open(file_name, 'w') as file:
    for item in full_zi:
        file.write(item + '\n')
