import os
import cv2

# --------------------------------------------------
# 📷 Initialize camera only for local environment
# --------------------------------------------------
camera = None
if os.environ.get("RENDER") != "true":
    camera = cv2.VideoCapture(0)


def get_frame():
    """
    Returns a camera frame if available.
    In cloud (Render), returns None safely.
    """

    # ☁️ Cloud environment: no camera available
    if camera is None:
        return None

    success, frame = camera.read()
    if not success:
        return None

    return frame
