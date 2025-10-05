import os
import numpy as np
from numpy.linalg import norm

def load_user_embeddings(folder="data/users"):
    user_embeddings = {}
    for file in os.listdir(folder):
        if file.endswith(".npy"):
            username = os.path.splitext(file)[0]
            emb = np.load(os.path.join(folder, file))
            user_embeddings[username] = emb
    return user_embeddings

def recognize_face(embedding, user_embeddings, threshold=0.5):
    max_sim = -1
    identity = "Unknown"
    for username, user_emb in user_embeddings.items():
        sim = np.dot(embedding, user_emb) / (norm(embedding) * norm(user_emb))
        if sim > max_sim:
            max_sim = sim
            identity = username
    if max_sim < threshold:
        identity = "Unknown"
    return identity
