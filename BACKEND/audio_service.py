import os
import speech_recognition as sr

# --------------------------------------------------
# 🔒 Cloud safety: Disable microphone on Render
# --------------------------------------------------
if os.environ.get("RENDER") == "true":
    recognizer = None
    microphone = None
else:
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

# --------------------------------------------------
# 🎤 Audio Cheating Detection
# --------------------------------------------------
def detect_audio_cheating():
    """
    Returns:
    - (True, text)   → Human speech detected (local PC)
    - (False, None)  → No speech / noise
    - (False, None)  → Cloud (audio disabled)
    """

    # ☁️ Cloud-safe
    if recognizer is None or microphone is None:
        return False, None

    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=3,
                phrase_time_limit=3
            )

        text = recognizer.recognize_google(audio)
        return True, text

    except sr.UnknownValueError:
        # Noise but no clear speech
        return False, None

    except (sr.WaitTimeoutError, sr.RequestError):
        return False, None
