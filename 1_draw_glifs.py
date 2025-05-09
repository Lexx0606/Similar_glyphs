from PIL import Image, ImageDraw, ImageFont
import os
from tqdm import tqdm

# file https://github.com/elkmovie/hsk30/charlist.txt needs a little manual processing
# Delete the headings and all parts of the list for the handwriting exam.
# There should be exactly 3000 characters left.
file_path = "dictionaries/hsk_zi.txt"
glifs_folder = "glifs/"


# use PIL to draw hieroglyphs
def drav_zi(han_zi):
    image = Image.new("RGB", (224, 224), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("ZhuqueFangsong-Regular.ttf", 220)
    draw.text((2, 2), han_zi, (0, 0, 0), font=font)
    output_path = glifs_folder + han_zi + ".png"
    # print (han_zi, output_path)
    image.save(output_path)


os.makedirs(glifs_folder, exist_ok=True)

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
                    drav_zi(char)

except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Error: {e}")

print("All hieroglyphs are drawn")
