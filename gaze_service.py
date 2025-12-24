import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def check_gaze(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks is None:
        return "NO_FACE"

    face = results.multi_face_landmarks[0]
    left_eye = face.landmark[33]
    right_eye = face.landmark[263]

    if abs(left_eye.x - right_eye.x) > 0.08:
        return "LOOKING_AWAY"

    return "LOOKING_FORWARD"
