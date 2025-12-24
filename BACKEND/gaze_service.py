import os
import cv2
import mediapipe as mp

# --------------------------------------------------
# 🔒 Cloud safety: Disable MediaPipe on Render
# --------------------------------------------------
if os.environ.get("RENDER") == "true":
    mp_face_mesh = None
    face_mesh = None
else:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

# --------------------------------------------------
# 👁️ Gaze Detection Function
# --------------------------------------------------
def check_gaze(frame):
    # Cloud / disabled mode
    if face_mesh is None or frame is None:
        return "DISABLED"

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return "NO_FACE"

    face = results.multi_face_landmarks[0]

    # Eye landmarks
    left_eye = face.landmark[33]
    right_eye = face.landmark[263]

    # Simple gaze heuristic
    if abs(left_eye.x - right_eye.x) > 0.08:
        return "LOOKING_AWAY"

    return "LOOKING_FORWARD"
