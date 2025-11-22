from flask import Flask, render_template, Response
import cv2
import numpy as np
import pickle
import csv
from datetime import datetime
import os
import time
import pandas as pd

app = Flask(__name__)

# ---------------- LOAD LBPH MODEL ----------------
MODEL_PATH = "model/lbph_model.yml"
LABELS_PATH = "model/lbph_labels.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(LABELS_PATH):
    raise FileNotFoundError("Run train_lbph.py first to train the model.")

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

with open(LABELS_PATH, "rb") as f:
    label_names = pickle.load(f)  # index -> name

print("[INFO] Loaded LBPH model with labels:", label_names)

# ---------------- ATTENDANCE SETUP ----------------
ATTENDANCE_PATH = "attendance/records.csv"
os.makedirs("attendance", exist_ok=True)

# make sure file exists with header
if not os.path.exists(ATTENDANCE_PATH):
    with open(ATTENDANCE_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "DateTime"])


def mark_attendance(name: str):
    """Mark attendance only once per day for each student."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if this name is already present today
    with open(ATTENDANCE_PATH, "r") as f:
        rows = csv.reader(f)
        next(rows, None)  # skip header
        for row in rows:
            if len(row) >= 2 and row[0] == name and row[1].startswith(today):
                print(f"[INFO] {name} already marked present today.")
                return  # don't write again

    # If not marked today, append a new record
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ATTENDANCE_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, now])

    print(f"[ATTENDANCE] Marked {name} at {now}")


# ---------------- FACE DETECTOR (HAAR) ----------------
haar_path = cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
face_cascade = cv2.CascadeClassifier(haar_path)
if face_cascade.empty():
    print("[WARN] Could not load Haar Cascade:", haar_path)

FACE_SIZE = (200, 200)
CONF_THRESHOLD = 95.0  # LBPH confidence; lower = better


# ---------------- VIDEO + RECOGNITION ----------------
def gen_frames():
    cap = cv2.VideoCapture(0)
    marked = set()  # not strictly needed now, but keeps spam down per session

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("[ERROR] Failed to capture frame.")
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 480))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]
            if face_roi.size == 0:
                continue

            face_roi = cv2.resize(face_roi, FACE_SIZE)

            label_id, confidence = recognizer.predict(face_roi)

            if confidence < CONF_THRESHOLD and 0 <= label_id < len(label_names):
                name = label_names[label_id]
                # we still keep per-session check to avoid re-print spam
                if name not in marked:
                    mark_attendance(name)
                    marked.add(name)
            else:
                name = "Unknown"

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{name} ({confidence:.1f})",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        time.sleep(0.01)


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/attendance")
def view_attendance():
    """Show attendance table using pandas."""
    if os.path.exists(ATTENDANCE_PATH):
        df = pd.read_csv(ATTENDANCE_PATH)
        records = df.to_dict(orient="records")
    else:
        records = []

    return render_template("attendance.html", records=records)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
