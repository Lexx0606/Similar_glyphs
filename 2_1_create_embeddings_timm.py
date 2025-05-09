import os
import sqlite3
from tqdm import tqdm
import timm
from PIL import Image
from typing import List
import struct
import numpy
import torch


# converting to bytes for saving in a real table
def serialize_f32(vector: List[float]) -> bytes:
    # serializes a list of floats into a compact "raw bytes" format
    return struct.pack("%sf" % len(vector), *vector)


# preparin image to transfering to cuda
def img_converion(img):
    channel_count = len(img.getbands())
    img = numpy.reshape(img, (channel_count, img.height, img.width))
    img = torch.from_numpy(img.astype(numpy.float32))
    img = img.cuda()
    return img


# path to the hieroglyphic images folder
folder_path = 'glifs'

# preparation of the embedding model
model = timm.create_model(
    'vit_large_patch14_dinov2.lvd142m',
    pretrained=True,
    num_classes=0,  # remove classifier nn.Linear
)
model = model.eval()
model.to('cuda')
data_config = timm.data.resolve_model_data_config(model)
transforms = timm.data.create_transform(**data_config, is_training=False)

# databse opening
conn = sqlite3.connect('zi.db')
cursor = conn.cursor()

# creating table
cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zi TEXT NOT NULL,
    pinyin TEXT,
    ru_short_art TEXT,
    ru_full_art TEXT,
    eng_art TEXT,
    hsk BOOLEAN,
    timm_embedding BLOB,
    res_embedding BLOB
)
''')

# getting full names for all files in folder
file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

# go through all files
with conn:
    for file_path in tqdm(file_list):
        # getting zi
        zi = file_path[6:7]
        img = Image.open(file_path)
        # transfer image to cuda
        img = img_converion(img)
        # getting embeddings
        output = model(transforms(img).unsqueeze(0))
        # converting embeddings to BLOB
        item = serialize_f32(output[0].tolist())
        conn.execute(
            "INSERT INTO files(zi, timm_embedding) VALUES (?, ?)",
            (zi, item)
        )
conn.close()

print("All embeddings have been added to the database")
