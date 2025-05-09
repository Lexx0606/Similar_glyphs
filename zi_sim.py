import sys
if sys.version_info[1] < 12:
    import sqlean as sqlite3
else:
    import sqlite3
import streamlit as st
import os
import sqlite_vec
import numpy as np
import struct
from pynput.keyboard import Key, Controller
import signal
import locale
# trying find russian
locale.setlocale(locale.LC_ALL, "")
locale_info = locale.getlocale()
user_lang = locale_info[0].split('_')[0]
lang_code = locale.normalize(user_lang)[:2].lower()

# Text strings
if lang_code == "ru":
    zi_title = "Поиск похожих иероглифов"
    zi_invit = "Введите иероглиф и нажмите Enter"
    base_error = "Ошибка при выполнении запроса:"
    find_eror = "Такой иероглиф не найде."
    find_count = "Всего отобрать иероглифов:"
    dist_text = """&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; Расстояние:"""
    turn_off = "Выход"
    radio_title = "Вид словарной статьи"
    ru_short_art = "Короткая русская"
    ru_full_art = "Длинная русская"
    eng_art = "Английская"
    embeding_radio_title = "Сортировать на основе эмбеддингов"
else:
    zi_title = "Search for similar hieroglyphs"
    zi_invit = "Type the hieroglyph and press Enter"
    base_error = "Request execution error:"
    find_eror = "The line with the specified hieroglyph was not found."
    find_count = "Total to select hieroglyphs:"
    dist_text = """&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; Distance:"""
    turn_off = "Shut Down"
    radio_title = "Type of dictionary entry"
    ru_short_art = "Short Russian"
    ru_full_art = "Long Russian"
    eng_art = "English"
    embeding_radio_title = "Sorting by embeddings"

timm_name = "Timm dino v2"
resnet_name = "ResNet50"
base_file = 'zi.db'
zi_style_set = """<p style="font-size: 60px; font-family: 'ZhuqueFangsong-Regular.ttf';">"""

st.set_page_config(page_title=zi_title, layout="wide")


# Converting a string of bytes back to vectors
def deserialize_f32(byte_string):
    # creating an empty array to store the results
    vec_count = len(byte_string)//4
    float_vector = np.empty(vec_count, dtype=np.float32)
    # go through each block of 4 bytes and convert it to a float number
    for i in range(vec_count):
        byte_block = byte_string[i*4:(i+1)*4]
        # use struct to converting
        float_value = struct.unpack('f', byte_block)[0]
        float_vector[i] = float_value
    return float_vector


# creating a virtual database in memory. Only it can work with vectors
db = sqlite3.connect(":memory:")
db.enable_load_extension(True)
sqlite_vec.load(db)
db.enable_load_extension(False)
db.execute("CREATE VIRTUAL TABLE vec_items USING vec0(zi TEXT, pinyin TEXT, ru_short_art TEXT, ru_full_art TEXT, eng_art TEXT, timm_embedding float[1024], res_embedding float[2048])")

# opening a real database
conn = sqlite3.connect(base_file)
cursor = conn.cursor()
# pulling out all the records
query = "SELECT * FROM files"
try:
    cursor.execute(query)
    rows = cursor.fetchall()
    # transfer each record to a virtual database
    for row in rows:
        db.execute(
           "INSERT INTO vec_items(zi, pinyin, ru_short_art, ru_full_art, eng_art, timm_embedding, res_embedding) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [row [1], row [2], row [3], row[4], row[5], row[7], row[8]],
        )
except sqlite3.Error as e:
    st.write(base_error, e)
finally:
    conn.close()
# window formation

st.title(zi_title)
exit_app = st.sidebar.button(turn_off)
if exit_app:
    # Close streamlit browser tab
    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press('w')
    keyboard.release('w')
    keyboard.release(Key.ctrl)
    # Terminate streamlit python process
    os.kill(os.getpid(), signal.SIGKILL)
st.sidebar.divider()
type_select = st.sidebar.radio (label = radio_title, options = [ru_short_art, ru_full_art, eng_art])
st.sidebar.divider()
embeding_select = st.sidebar.radio (label = embeding_radio_title, options = [timm_name, resnet_name])


col1, col2 = st.columns(2)
with col1:
    zi = st.text_input(zi_invit, "时", max_chars=1)
    if '\u4e00' >= zi >= '\u9fff':  # the range of hieroglyphs in UTF-8
        zi = "时"
with col2:
    zi_count = st.number_input(find_count, value=50, min_value=1, max_value=100)
if type_select == ru_short_art:
    d_type = "ru_short_art"
elif type_select == ru_full_art:
    d_type = "ru_full_art"
else:
    d_type = "eng_art"

if embeding_select == timm_name:
    result = db.execute("SELECT timm_embedding FROM vec_items WHERE zi=?", (zi,)).fetchone()
    if result:
        # If a row is found, output the corresponding value from the embedding column
        query = result[0]
        rows = db.execute("""SELECT zi, distance, pinyin, ru_short_art, ru_full_art, eng_art FROM vec_items WHERE timm_embedding MATCH ? ORDER BY distance LIMIT ?""", [deserialize_f32(query), zi_count],).fetchall()
    else:
        st.error(find_eror)
else:
    result = db.execute("SELECT res_embedding FROM vec_items WHERE zi=?", (zi,)).fetchone()
    if result:
        # If a row is found, output the corresponding value from the embedding column
        query = result[0]
        rows = db.execute("""SELECT zi, distance, pinyin, ru_short_art, ru_full_art, eng_art FROM vec_items WHERE res_embedding MATCH ? ORDER BY distance LIMIT ?""", [deserialize_f32(query), zi_count],).fetchall()
    else:
        st.error(find_eror)


four_col = []
for row in rows:
    four_col.append(row[0])
    four_col.append(row[1])
    four_col.append(row[2])
    if type_select == ru_short_art:
        four_col.append(row[3])
    elif type_select == ru_full_art:
        four_col.append(row[4])
    else:
        four_col.append(row[5])
    # two-column display
    if len(four_col) == 8:
        col1, col2, col3, col4 = st.columns([1, 10, 1, 10])
        with col1:
            prtbl = zi_style_set + four_col[0]
            st.write(prtbl, unsafe_allow_html=True)
        with col2:
            st.write(four_col[2], dist_text, four_col[1], unsafe_allow_html=True)
            st.write(four_col[3], unsafe_allow_html=True)
        with col3:
            prtbl = zi_style_set + four_col[4]
            st.write(prtbl, unsafe_allow_html=True)
        with col4:
            st.write(four_col[6], dist_text, four_col[5])
            st.write(four_col[7], unsafe_allow_html=True)
        four_col = []
if len(four_col) == 4:
    col1, col2 = st.columns([1, 21])
    with col1:
        prtbl = zi_style_set + four_col[0]
        st.write(prtbl, unsafe_allow_html=True)
    with col2:
        st.write(four_col[2], dist_text, four_col[1])
        st.write(four_col[3], unsafe_allow_html=True)
