from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim
_INDEX_DIM = 512                                        # your Pinecone index dim

_model = SentenceTransformer(_MODEL_NAME)

def _pad_to_index_dim(vec: np.ndarray) -> np.ndarray:
    """Zero-pad (or truncate) a 1D vector to _INDEX_DIM."""
    d = vec.shape[0]
    if d == _INDEX_DIM:
        return vec
    if d > _INDEX_DIM:
        return vec[:_INDEX_DIM]
    out = np.zeros(_INDEX_DIM, dtype=np.float32)
    out[:d] = vec
    return out

def embed_text(text: str) -> list[float]:
    """Embed a single string → 512-dim (list of floats)."""
    v = _model.encode([text], normalize_embeddings=True)[0]  # shape (384,)
    v512 = _pad_to_index_dim(np.asarray(v, dtype=np.float32))
    return v512.tolist()

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch embed → list of 512-dim vectors."""
    vs = _model.encode(texts, normalize_embeddings=True)     # (N, 384)
    return [_pad_to_index_dim(np.asarray(v, dtype=np.float32)).tolist() for v in vs]
