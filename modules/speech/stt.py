# import speech_recognition as sr

# class SpeechToText:
#     def __init__(self, mic_index=None):
#         self.recognizer = sr.Recognizer()
#         self.mic_index = mic_index
#         print(f"[DEBUG] Initialized SpeechToText with mic index {mic_index}")

#     def calibrate_microphone(self, duration: int = 2):
#         """Adjust energy threshold to ambient noise."""
#         with sr.Microphone(device_index=self.mic_index) as source:
#             print("[DEBUG] Calibrating microphone, please stay quiet...")
#             self.recognizer.adjust_for_ambient_noise(source, duration=duration)
#             print(f"[DEBUG] Calibration complete. Energy threshold = {self.recognizer.energy_threshold}")

#     def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
#         """Listen for speech and return recognized text."""
#         with sr.Microphone(device_index=self.mic_index) as source:
#             print(f"[DEBUG] Listening... (timeout={timeout}, phrase_time_limit={phrase_time_limit})")
#             audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

#         try:
#             text = self.recognizer.recognize_google(audio)
#             print(f"[DEBUG] Recognized speech: {text}")
#             return text
#         except sr.UnknownValueError:
#             print("[DEBUG] Could not understand audio")
#             return ""
#         except sr.RequestError as e:
#             print(f"[DEBUG] API unavailable: {e}")
#             return ""

# def list_microphones():
#     """List available microphones."""
#     return sr.Microphone.list_microphone_names()
import speech_recognition as sr
import threading
import queue
import asyncio

def list_microphones():
    """Return a list of available microphone names."""
    return sr.Microphone.list_microphone_names()

class StreamingSTT:
    def __init__(self, mic_index=0):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(device_index=mic_index)
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None

    def _callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio)
            self.queue.put(text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"[ERROR] Speech recognition service error: {e}")

    def start(self):
        """Start background listening in a thread."""
        if self.thread is not None:
            return
        self.thread = self.recognizer.listen_in_background(
            self.mic, self._callback
        )

    def stop(self):
        """Stop listening."""
        if self.thread is not None:
            self.thread(wait_for_stop=False)
            self.thread = None
        self.stop_event.set()

    async def listen_and_transcribe(self):
        """Async generator that yields recognized phrases in real time."""
        while not self.stop_event.is_set():
            try:
                text = self.queue.get_nowait()
                yield text
            except queue.Empty:
                await asyncio.sleep(0.1)  # avoid busy loop
