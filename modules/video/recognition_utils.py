import os
import numpy as np
from numpy.linalg import norm

def load_user_embeddings(folder="data/users"):
    """
    Load all embeddings for all users.
    Returns a dictionary:
    {
        username: [embedding1, embedding2, ...],
        ...
    }
    """
    user_embeddings = {}
    for username in os.listdir(folder):
        user_folder = os.path.join(folder, username)
        if os.path.isdir(user_folder):
            embeddings = []
            for file in os.listdir(user_folder):
                if file.endswith(".npy"):
                    emb = np.load(os.path.join(user_folder, file))
                    embeddings.append(emb)
            if embeddings:
                user_embeddings[username] = embeddings
    return user_embeddings

def recognize_face(embedding, user_embeddings, threshold=0.3):
    """
    Compare live embedding against all stored embeddings for all users.
    Returns the matched username or 'Unknown'.
    """
    max_sim = -1
    identity = "Unknown"

    for username, embeddings_list in user_embeddings.items():
        for user_emb in embeddings_list:
            sim = np.dot(embedding, user_emb) / (norm(embedding) * norm(user_emb))
            if sim > max_sim:
                max_sim = sim
                identity = username

    if max_sim < threshold:
        identity = "Unknown"

    return identity
