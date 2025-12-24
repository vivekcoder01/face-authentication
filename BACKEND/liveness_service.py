import os
import cv2
import mediapipe as mp

# --------------------------------------------------
# 🔒 Cloud safety: Disable MediaPipe on Render
# --------------------------------------------------
if os.environ.get("RENDER") == "true":
    face_mesh = None
else:
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

# --------------------------------------------------
# 👁️ Blink / Liveness Detection
# --------------------------------------------------
def detect_blink(frame):
    """
    Returns:
    - True / False  → Local PC (blink detected or not)
    - 'DISABLED'    → Cloud (Render)
    - 'NO_FACE'     → Face not detected
    """

    # ☁️ Cloud-safe
    if face_mesh is None or frame is None:
        return "DISABLED"

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return "NO_FACE"

    face = results.multi_face_landmarks[0]

    # Eye landmarks (upper & lower eyelid)
    top = face.landmark[159]
    bottom = face.landmark[145]

    # Blink threshold
    return abs(top.y - bottom.y) < 0.004
