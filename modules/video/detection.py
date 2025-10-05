import os
import time
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from threading import Lock

#Utils
def cosine_similarity(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
    return float(np.dot(a, b) / denom)

#Config 
USERS_DIR = "data/users"       # folders per user, each contains a few face images
EMB_THRESHOLD = 0.60           # similarity threshold
IDLE_SECONDS = 7               # how long without a face before we mark idle

#Globals (shared state)
lock = Lock()
current_user = None
system_active = False
_last_seen = 0.0
_user_embeddings = {}

#ArcFace
print("[DETECTION] Loading ArcFace...")
_app = FaceAnalysis(name="buffalo_l")

try:
    _app.prepare(ctx_id=0)   # try GPU
    print("[DETECTION] Using GPU for face recognition")
except Exception as e:
    print("[DETECTION] GPU failed, falling back to CPU:", e)
    _app.prepare(ctx_id=-1)  # fallback CPU

# Precompute User Embeddings
print("[DETECTION] Precomputing user embeddings...")
for username in os.listdir(USERS_DIR):
    user_path = os.path.join(USERS_DIR, username)
    if not os.path.isdir(user_path):
        continue
    embs = []
    for f in os.listdir(user_path):
        img_path = os.path.join(user_path, f)
        if not os.path.isfile(img_path):
            continue
        img = cv2.imread(img_path)
        if img is None:
            continue
        faces = _app.get(img)  # expects BGR
        if not faces:
            continue
        embs.append(faces[0].normed_embedding)
    if embs:
        _user_embeddings[username] = embs

print(f"[DETECTION] Users loaded: {list(_user_embeddings.keys()) or '[none]'}")


def _match_user(emb: np.ndarray) -> str | None:
    """Return best-matching username or None."""
    best_user = None
    best_sim = 0.0
    for user, emb_list in _user_embeddings.items():
        for ref in emb_list:
            sim = cosine_similarity(emb, ref)
            if sim > best_sim:
                best_sim = sim
                best_user = user
    if best_sim >= EMB_THRESHOLD:
        return best_user
    return None


def process_frame(frame):
    """
    Update internal state based on a single frame and return (user, active).
    frame: numpy array (BGR) from cv2.imdecode
    """
    global current_user, system_active, _last_seen

    # Detect faces
    faces = _app.get(frame)
    print(f"[DEBUG] Faces detected: {len(faces)}")   # LOGGING

    recognized = None

    if faces:
        emb = faces[0].normed_embedding
        recognized = _match_user(emb)
        if recognized:
            print(f"[DEBUG] Recognized user: {recognized}")
            _last_seen = time.time()
            with lock:
                current_user = recognized
                system_active = True
        else:
            print("[DEBUG] Unknown face detected")
            _last_seen = time.time()
            with lock:
                current_user = None
                system_active = True
    else:
        if time.time() - _last_seen > IDLE_SECONDS:
            with lock:
                current_user = None
                system_active = False
            print("[DEBUG] No face for a while → system idle")

    with lock:
        return current_user, system_active
