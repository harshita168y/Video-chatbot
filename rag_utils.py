import os
import logging
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_utils")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "video-chatbot")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"   # ✅ 384 dimensions

if not PINECONE_API_KEY:
    raise ValueError("❌ Missing PINECONE_API_KEY in environment.")

pc = Pinecone(api_key=PINECONE_API_KEY)

logger.info(f"🧠 Loading embedding model: {EMBED_MODEL_NAME}")
embedder = SentenceTransformer(EMBED_MODEL_NAME)

DIM = embedder.get_sentence_embedding_dimension()  # should be 384
try:
    if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
        logger.info(f"📦 Creating Pinecone index '{INDEX_NAME}' (dim={DIM})...")
        pc.create_index(
            name=INDEX_NAME,
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
                dimension=DIM,
                metric="cosine"
            )
        )
    logger.info(f"🔗 Connected to Pinecone index: {INDEX_NAME}")
except Exception as e:
    logger.error(f"❌ Error ensuring Pinecone index: {e}")
    raise

# Index handle
index = pc.Index(INDEX_NAME)

def get_embedding(text: str):
    """Convert text to vector embedding (384-dim)."""
    return embedder.encode(text).tolist()


def upsert_memory(user_id: str, text: str):
    """Store message in Pinecone."""
    try:
        vector = get_embedding(text)
        index.upsert([
            (f"{user_id}-{hash(text)}", vector, {"text": text})
        ])
        logger.info(f"✅ Upserted message for user={user_id}")
    except Exception as e:
        logger.error(f"❌ Pinecone upsert failed: {e}")


def query_memory(query: str, top_k: int = 3):
    """Retrieve top_k relevant messages from Pinecone."""
    try:
        vector = get_embedding(query)
        res = index.query(vector=vector, top_k=top_k, include_metadata=True)
        logger.info(f"🔍 Query results: {len(res.get('matches', []))} matches")
        return res
    except Exception as e:
        logger.error(f"❌ Pinecone query failed: {e}")
        return {"matches": []}
