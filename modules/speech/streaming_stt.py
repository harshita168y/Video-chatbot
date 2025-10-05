# import collections
# import queue
# import numpy as np
# import sounddevice as sd
# import webrtcvad
# from faster_whisper import WhisperModel


# class StreamingSTT:
#     def __init__(self, model_size="base", device="cpu", mic_index=None, vad_aggressiveness=2):
#         # Load Whisper
#         self.model = WhisperModel(model_size, device=device, compute_type="int8")

#         # Setup audio capture
#         self.samplerate = 16000
#         self.block_size = 30  # ms
#         self.vad = webrtcvad.Vad(vad_aggressiveness)

#         self.buffer = collections.deque()
#         self.audio_queue = queue.Queue()

#         self.stream = sd.RawInputStream(
#             samplerate=self.samplerate,
#             blocksize=int(self.samplerate * self.block_size / 1000),
#             device=mic_index,
#             dtype="int16",
#             channels=1,
#             callback=self._audio_callback,
#         )

#     def _audio_callback(self, indata, frames, time, status):
#         if status:
#             print(f"[STT WARNING] {status}")
#         self.audio_queue.put(bytes(indata))

#     def listen_and_transcribe(self, phrase_timeout=1.0):
#         """
#         Continuously listens and yields transcriptions whenever a phrase ends.
#         """
#         self.stream.start()
#         print("[DEBUG] Streaming STT started...")

#         ring_buffer = collections.deque(maxlen=10)
#         triggered = False
#         voiced_frames = []
#         last_speech_time = None

#         while True:
#             frame = self.audio_queue.get()
#             is_speech = self.vad.is_speech(frame, self.samplerate)

#             if not triggered:
#                 ring_buffer.append((frame, is_speech))
#                 num_voiced = len([f for f, speech in ring_buffer if speech])
#                 if num_voiced > 0.9 * ring_buffer.maxlen:
#                     triggered = True
#                     voiced_frames.extend([f for f, s in ring_buffer])
#                     ring_buffer.clear()
#             else:
#                 voiced_frames.append(frame)
#                 ring_buffer.append((frame, is_speech))
#                 num_unvoiced = len([f for f, speech in ring_buffer if not speech])

#                 if num_unvoiced > 0.9 * ring_buffer.maxlen:
#                     audio_data = b"".join(voiced_frames)
#                     np_audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

#                     # Run Whisper transcription
#                     segments, _ = self.model.transcribe(np_audio, beam_size=1)
#                     text = " ".join([seg.text for seg in segments]).strip()

#                     if text:
#                         yield text

#                     triggered = False
#                     voiced_frames = []
#                     ring_buffer.clear()
import speech_recognition as sr
import asyncio

class StreamingSTT:
    def __init__(self, mic_index=0):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(device_index=mic_index)
        print(f"[DEBUG] Initialized StreamingSTT with mic index {mic_index}")

    async def listen_and_transcribe(self):
        loop = asyncio.get_event_loop()
        with self.mic as source:
            print("[DEBUG] Calibrating microphone, please stay quiet...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("[DEBUG] Calibration complete. Start talking...")

            while True:
                try:
                    # Listen in background, but without timeout
                    audio = await loop.run_in_executor(None, self.recognizer.listen, source)

                    # Send audio to Google recognizer
                    text = await loop.run_in_executor(None, self.recognizer.recognize_google, audio)
                    print(f"You said: {text}")
                    yield text

                except sr.UnknownValueError:
                    print("[DEBUG] Could not understand audio")
                    yield ""
                except sr.RequestError as e:
                    print(f"[ERROR] API unavailable: {e}")
                    yield ""
                except Exception as e:
                    print(f"[ERROR] STT failed: {e}")
                    yield ""

