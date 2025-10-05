# Video-chatbot
An AI-powered Video + RAG Chatbot that recognizes faces, remembers past conversations via Pinecone, and chats naturally using Ollama or OpenAI — all in real time. Built with FastAPI, InsightFace, and Retrieval-Augmented Generation (RAG) for a human-like multimodal experience.

🎥 Video + RAG Chatbot (with Face Recognition & Memory)
A multimodal AI assistant that combines:

> Real-time face recognition (via InsightFace)

> Natural conversation through local LLMs (Ollama or OpenAI)

> Long-term memory using Pinecone + embeddings

> Optional speech support (STT + TTS)

> Built on FastAPI, WebSockets, and Python

⚙️ Setup
> 1️) Clone the repo
git clone https://github.com/<your-username>/video-rag-chatbot.git
cd video-rag-chatbot

> 2️) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

> 3️) Install dependencies
pip install -r requirements.txt

> 4️) Set up your .env
Create a .env file in the root directory:
Pinecone:
PINECONE_API_KEY=pcsk_
PINECONE_INDEX=video-chatbot
LLM (choose one)
OLLAMA_URL=http://localhost:11434/api/generate
or, if using OpenAI:
OPENAI_API_KEY=sk-proj-

🚀 Running the Server
uvicorn server:app --reload

Then visit:
http://127.0.0.1:8000/docs
for the interactive Swagger UI.


📸 Face Recognition Workflow
Each frame from the webcam is:
>Sent via WebSocket → /video-stream

>Processed by detection.py using ArcFace

>Matched to stored user embeddings in data/users/

>Response: { "user": "name", "active": true }

Embeddings
EMBED_MODEL=all-MiniLM-L6-v2
