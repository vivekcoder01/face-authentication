import speech_recognition as sr
import numpy as np

recognizer = sr.Recognizer()
mic = sr.Microphone()

def detect_audio_cheating():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            text = recognizer.recognize_google(audio)
            return True, text   # Human voice detected
        except sr.UnknownValueError:
            return False, None  # Noise but no clear speech
        except sr.WaitTimeoutError:
            return False, None
