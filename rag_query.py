# rag_query.py
from pinecone import Pinecone
from modules.rag.embeddings import embed_text

# Connect to Pinecone
pc = Pinecone(api_key="pcsk_5m4ABP_DopP7v9TWusvzEFKpNwNn3P6hXASBXfiXcbuDuXb7QNAC6MZNu26BSfbEFoZjA8")
index = pc.Index("chatbot")  # your index name

# Ask a question
query = "What is my name?"
vector = embed_text(query)   # ✅ already a list

# Query Pinecone
results = index.query(vector=vector, top_k=3, include_metadata=True)
print("🔎 Query results:", results)
