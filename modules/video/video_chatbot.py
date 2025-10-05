import time
import queue
import json
import threading
import numpy as np
import sounddevice as sd
from gtts import gTTS
from playsound import playsound
import os

import modules.video.detection as detection
from modules.nlp.assistant import Assistant
import vosk

# Audio Setup
MODEL_PATH = r"C:\Users\harsh\video_chatbot\models\vosk"
RATE = 16000

print("[DEBUG] Loading Vosk model...")
vosk_model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(vosk_model, RATE)

q = queue.Queue()

# TTS (gTTS + playsound)
tts_thread = None
tts_stop_flag = threading.Event()

def stop_tts():
    """Stop ongoing TTS if user interrupts"""
    global tts_thread, tts_stop_flag
    if tts_thread and tts_thread.is_alive():
        print("[DEBUG] TTS interrupted")
        tts_stop_flag.set()
        tts_thread.join()
    tts_stop_flag.clear()
    tts_thread = None

def play_tts(text):
    """Speak text using gTTS, interruptible"""
    def _run():
        try:
            tts = gTTS(text=text, lang="en")
            filename = "temp_reply.mp3"
            tts.save(filename)

            if not tts_stop_flag.is_set():
                playsound(filename, block=True)

            os.remove(filename)
        except Exception as e:
            print(f"[ERROR] TTS playback failed: {e}")

    global tts_thread
    stop_tts()
    tts_thread = threading.Thread(target=_run, daemon=True)
    tts_thread.start()

# Mic callback

def callback(indata, frames, time, status):
    if status:
        print("[ERROR]", status, flush=True)

    audio_data = np.frombuffer(indata, dtype=np.int16)
    volume_norm = np.linalg.norm(audio_data) / len(audio_data)

    # stop TTS if user starts speaking
    if volume_norm > 50:
        stop_tts()

    q.put(bytes(indata))

# Video Chatbot Main Loop

def run_video_chatbot(idle_timeout: int = 60):
    print("=== Video Chatbot (Ollama + Face Recognition + Vosk STT) ===")

    # Start video detection
    print("\n[DEBUG] Starting video detection...")
    detection.start_video_recognition()
    print("\nSystem ready. Waiting for a recognized face...\n")

    assistant = Assistant()
    session_active = False
    user_name = None
    last_interaction = time.time()

    with sd.RawInputStream(samplerate=RATE, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print("[DEBUG] Mic stream ready. Listening continuously...")

        while True:
            # Face detection
            with detection.lock:
                active = detection.system_active
                user = detection.current_user

            # Face recognized → greet
            if active and not session_active and user:
                session_active = True
                user_name = user
                print(f"\nHello {user_name}! 👋")
                play_tts(f"Hello {user_name}, how can I help you?")
                last_interaction = time.time()

            if not session_active:
                time.sleep(0.2)
                continue

            # Idle timeout
            if time.time() - last_interaction > idle_timeout:
                print("[DEBUG] Idle timeout. Ending session.")
                play_tts("Going idle now. Goodbye!")
                break

            # Process audio from queue
            if not q.empty():
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print("You said:", text)
                        last_interaction = time.time()

                        if text.lower() in ["exit", "quit", "stop"]:
                            print("[DEBUG] Exit command. Shutting down.")
                            play_tts("Goodbye!")
                            break

                        # Ask model
                        reply = assistant.ask_model(text)
                        print("Model:", reply)

                        # Speak reply
                        play_tts(reply)

                else:
                    partial = json.loads(rec.PartialResult())
                    if partial.get("partial"):
                        print("[DEBUG] Partial:", partial["partial"])
