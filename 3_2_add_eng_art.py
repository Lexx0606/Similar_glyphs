import sqlite3
from tqdm import tqdm

# open tables
conn_files = sqlite3.connect('zi.db')
cursor_files = conn_files.cursor()
conn_ed = sqlite3.connect('eng_dict.db')
cursor_ed = conn_ed.cursor()

# getting zi from files
cursor_files.execute("SELECT zi FROM files")
zi_values = cursor_files.fetchall()

# go through all zi
for zi in tqdm(zi_values):
    zi_value = zi[0]  # get zi

    # getting article from dict
    query = "SELECT eng_art FROM eng_dict WHERE zi = ?"
    cursor_ed.execute(query, (zi_value,))

    # if no result add - instead of article
    result = cursor_ed.fetchone()
    if result:
        eng_art = result[0]
    else:
        eng_art = "-"
    # updating files
    update_query = "UPDATE files SET eng_art = ? WHERE zi = ?"
    cursor_files.execute(update_query, (eng_art, zi_value))
    conn_files.commit()

# closing connections
cursor_files.close()
conn_files.close()
cursor_ed.close()
conn_ed.close()
