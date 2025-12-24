import cv2
import pickle
from face_recognition_cnn import get_embedding

cap = cv2.VideoCapture(0)
embeddings = {}

name = input("Enter candidate name: ")

print("Capturing face... Press Q to save")
while True:
    ret, frame = cap.read()
    cv2.imshow("Capture Face", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        embedding = get_embedding(frame)
        embeddings[name] = embedding
        break

cap.release()
cv2.destroyAllWindows()

with open("embeddings.pkl", "wb") as f:
    pickle.dump(embeddings, f)

print("Face registered successfully")
