import os
from pinecone import Pinecone
from modules.rag.embeddings import embed_text

pc = Pinecone(api_key="pcsk_5m4ABP_DopP7v9TWusvzEFKpNwNn3P6hXASBXfiXcbuDuXb7QNAC6MZNu26BSfbEFoZjA8")
index = pc.Index("chatbot")  # your Pinecone index name  # your index name

docs = [
    "Harshita said she likes watching movies on weekends.",
    "Harshita enjoys coding in Python.",
    "Harshita recently started learning about RAG systems.",
]

vectors = []
for i, doc in enumerate(docs):
    vec = embed_text(doc)
    vectors.append((f"doc-{i}", vec, {"text": doc}))

index.upsert(vectors)
print("✅ Inserted", len(docs), "vectors into Pinecone")
