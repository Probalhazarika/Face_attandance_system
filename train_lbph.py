import os
import cv2
import numpy as np
import pickle

# Paths
IMAGE_DIR = "model/student_images"
MODEL_PATH = "model/lbph_model.yml"
LABELS_PATH = "model/lbph_labels.pkl"

# Haar cascade for cropping faces from training images
haar_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_path)

if face_cascade.empty():
    print("[ERROR] Could not load Haar cascade.")
    exit(1)

images = []
labels = []
label_names = []   # index -> name

face_size = (200, 200)
current_label = 0

for name in os.listdir(IMAGE_DIR):
    if name.startswith("."):
        continue

    folder = os.path.join(IMAGE_DIR, name)
    if not os.path.isdir(folder):
        continue

    print(f"[INFO] Processing person: {name}")

    for img_name in os.listdir(folder):
        if img_name.startswith("."):
            continue

        img_path = os.path.join(folder, img_name)
        img = cv2.imread(img_path)

        if img is None:
            print("  [WARN] Could not read image:", img_path)
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        if len(faces) == 0:
            print("  [WARN] No face found in:", img_name)
            continue

        # take the first detected face
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y + h, x:x + w]
        face_roi = cv2.resize(face_roi, face_size)

        images.append(face_roi)
        labels.append(current_label)

    if images:
        label_names.append(name)
        current_label += 1

if len(images) == 0:
    print("[ERROR] No training images found with faces.")
    exit(1)

print(f"[INFO] Total training samples: {len(images)}")
images = np.array(images, dtype="uint8")
labels = np.array(labels, dtype="int32")

# Create and train LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(images, labels)

os.makedirs("model", exist_ok=True)
recognizer.write(MODEL_PATH)

with open(LABELS_PATH, "wb") as f:
    pickle.dump(label_names, f)

print("[INFO] Training complete.")
print("[INFO] Saved model to", MODEL_PATH)
print("[INFO] Saved label mapping to", LABELS_PATH)
