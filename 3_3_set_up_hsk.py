# file https://github.com/elkmovie/hsk30/charlist.txt needs a little manual processing
# Delete the headings and all parts of the list for the handwriting exam.
# There should be exactly 3000 characters left.

import sqlite3
from tqdm import tqdm
file_path = "dictionaries/hsk_zi.txt"
conn_files = sqlite3.connect('try.db')
cursor_files = conn_files.cursor()

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in tqdm(file):
            # removing the spaces at the end of the line
            line = line.strip()
            # go through each character in the string
            for char in line:
                # check whether the symbol is a hieroglyph
                if '\u4e00' <= char <= '\u9fff':
                    # the range of hieroglyphs in UTF-8
                    update_query = "UPDATE files SET hsk = ? WHERE zi = ?"
                    cursor_files.execute(update_query, (True, char))
                    conn_files.commit()

except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Error: {e}")

cursor_files.close()
conn_files.close()
