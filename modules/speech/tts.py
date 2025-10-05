# import asyncio
# import edge_tts
# import sounddevice as sd
# import soundfile as sf
# import tempfile
# import os

# # Default voice (you can change this to any supported voice, e.g. en-GB-RyanNeural)
# VOICE = "en-US-AriaNeural"

# async def _speak_async(text: str, voice: str = VOICE):
#     """
#     Internal async function that generates speech using Edge TTS and plays it.
#     """
#     try:
#         # Save to a temporary file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
#             tmp_path = tmpfile.name

#         communicate = edge_tts.Communicate(text, voice)
#         await communicate.save(tmp_path)

#         # Play audio
#         data, samplerate = sf.read(tmp_path)
#         sd.play(data, samplerate)
#         sd.wait()

#         # Clean up
#         os.remove(tmp_path)

#     except Exception as e:
#         print(f"[ERROR] TTS failed: {e}")

# def speak(text: str, voice: str = VOICE):
#     """
#     Public function to speak text (synchronous wrapper).
#     Call this from main chatbot.
#     """
#     print(f"[DEBUG] Speaking with Edge TTS: {text}")
#     asyncio.run(_speak_async(text, voice))
# modules/speech/tts.py
# modules/speech/tts.py
# modules/speech/tts.py
from gtts import gTTS
import playsound
import tempfile
import os

def speak(text: str):
    try:
        tts = gTTS(text=text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            filename = fp.name
            tts.save(filename)
        print(f"[DEBUG] Speaking: {text}")
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")

        print(f"[DEBUG] Spoke: {text}")

    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")
