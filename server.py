import os
import cv2
import base64
import numpy as np
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Local modules
from rag_utils import upsert_memory, query_memory
from modules.video import detection  # face recognition module


load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")  # change if you want

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "🚀 Video + RAG Chatbot Server running"}


class ChatRequest(BaseModel):
    text: str
    user: str = "default-user"

@app.post("/chat")
async def chat(req: ChatRequest):
    """
    RAG-powered text chat (no video).
    - Upserts user message to Pinecone
    - Retrieves relevant context
    - Calls Ollama (non-stream) with the context
    - Upserts bot reply back to Pinecone
    """
    user_text = (req.text or "").strip()
    user_id = req.user or "default-user"

    if not user_text:
        return {"reply": "I didn't receive any input."}


    upsert_memory(user_id, user_text)

    context_results = query_memory(user_text, top_k=3)
    context_texts = [m["metadata"]["text"] for m in context_results.get("matches", [])]
    context = "\n".join(context_texts)

    prompt = (
        "You are a helpful assistant. Use the context when relevant; "
        "if it’s not relevant, answer normally.\n\n"
        f"Context:\n{context}\n\n"
        f"User: {user_text}\nBot:"
    )
    payload = {
        "model": OLLAMA_MODEL,
        # "prompt": prompt,
         "prompt": (
            "You are a helpful and context-aware AI assistant.\n"
            "Below is memory retrieved from past conversations. "
            "Use this context strictly when answering — do not make things up.\n\n"
            f"--- MEMORY ---\n{context}\n"
            "----------------\n\n"
            f"User: {user_text}\n"
            "Bot (based only on the memory and conversation history):"
        ),
        "stream": False,     
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            llm_reply = (data.get("response") or "").strip()
            if not llm_reply:
                llm_reply = "I couldn't generate a response."
        else:
            llm_reply = f"⚠️ LLM error (HTTP {resp.status_code})."
    except Exception as e:
        llm_reply = f"⚠️ Backend error: {e}"

 
    upsert_memory("bot", llm_reply)

    return {"reply": llm_reply, "context": context_texts}

@app.websocket("/video-stream")
async def video_stream(websocket: WebSocket):
    """
    Frontend sends JPEG base64 (no data URL prefix).
    We decode -> OpenCV frame (BGR) -> detection.process_frame(frame)
    Send back: {"user": <name or None>, "active": <bool>}
    """
    await websocket.accept()
    print("[WS] Video stream connected ✅")
    try:
        while True:
          
            b64 = await websocket.receive_text()
            try:
                img_bytes = base64.b64decode(b64)
                img_array = np.frombuffer(img_bytes, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if frame is None:
                 
                    await websocket.send_json({"user": None, "active": False})
                    continue
            except Exception:
           
                await websocket.send_json({"user": None, "active": False})
                continue

            user, active = detection.process_frame(frame)

            await websocket.send_json({"user": user, "active": active})

    except WebSocketDisconnect:
        print("[WS] Client disconnected ❌")
    except Exception as e:
        print(f"[WS] Error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass
