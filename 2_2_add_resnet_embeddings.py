from tqdm import tqdm
import os
import sqlite3
from PIL import Image
from typing import List
import struct
import onnxruntime
from torchvision import transforms
import requests


# converting to bytes for saving in a real table
def serialize_f32(vector: List[float]) -> bytes:
    # serializes a list of floats into a compact "raw bytes" format
    return struct.pack("%sf" % len(vector), *vector)


def load_and_preprocess_image(image_path):
    # Define the same preprocessing as used in training
    preprocess = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    # Open the image file
    img = Image.open(image_path)
    # Preprocess the image
    img_preprocessed = preprocess(img)
    # Add batch dimension
    return img_preprocessed.unsqueeze(0).numpy()


# preparation of the embedding model
onnx_model_path = "resnet50_embeddings.onnx"
if not os.path.exists(onnx_model_path):
    response = requests.get('https://huggingface.co/jxtc/resnet-50-embeddings/blob/main/resnet50_embeddings.onnx')
    if response.status_code == 200:
        with open(onnx_model_path, 'wb') as file:
            file.write(response.content)
    else:
        print("Error when uploading the onnx model weights file")
        exit()
session = onnxruntime.InferenceSession(onnx_model_path)
input_name = session.get_inputs()[0].name

# path to the hieroglyphic images folder
folder_path = 'glifs'

# databse opening
conn = sqlite3.connect('zi.db')
cursor = conn.cursor()

# getting full names for all files in folder
file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

# go through all files
with conn:
    for file_path in tqdm(file_list):
        zi = file_path[6:7]
        input_data = load_and_preprocess_image(file_path)
        # Run inference
        outputs = session.run(None, {input_name: input_data})
        # The output should be a single tensor (the embeddings)
        embedding = outputs[0]
        # Flatten the embeddings
        embedding = embedding.reshape(embedding.shape[0], -1)
        # cinverting embeddings to BLOB
        item = serialize_f32(embedding[0])
        conn.execute(
            "UPDATE files SET res_embedding = ? WHERE zi = ?",
            (item, zi)
        )
conn.close()

print("All embeddings have been added to the database")
