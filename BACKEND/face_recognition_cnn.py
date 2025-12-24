import cv2
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from cnn_model import load_cnn_model

model = load_cnn_model()

def preprocess(face):
    face = cv2.resize(face, (160, 160))
    face = face.astype("float32") / 255.0
    return np.expand_dims(face, axis=0)

def get_embedding(face_img):
    processed = preprocess(face_img)
    embedding = model.predict(processed)
    return embedding

def verify_face(face_img):
    embedding = get_embedding(face_img)

    with open("embeddings.pkl", "rb") as f:
        known_embeddings = pickle.load(f)

    for name, saved_embedding in known_embeddings.items():
        similarity = cosine_similarity(embedding, saved_embedding)[0][0]
        if similarity > 0.75:
            return True, name

    return False, "Unknown"
