import cv2
import os
import pickle
import time
from app.repositories.attendance_repository import AttendanceRepository

# Load Model Global
MODEL_PATH = "model/lbph_model.yml"
LABELS_PATH = "model/lbph_labels.pkl"

recognizer = None
label_names = {}
face_cascade = None

def load_model():
    global recognizer, label_names, face_cascade
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LABELS_PATH):
        print("[WARN] Model not found. Face recognition will not work.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    with open(LABELS_PATH, "rb") as f:
        label_names = pickle.load(f)

    haar_path = cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
    face_cascade = cv2.CascadeClassifier(haar_path)
    print("[INFO] Loaded LBPH model and Haar cascade.")

# Initialize on import (or could be lazy loaded)
load_model()

class AttendanceService:
    @staticmethod
    def get_attendance_stats(subject_id):
        records = AttendanceRepository.get_records_by_subject(subject_id)
        total_classes = AttendanceRepository.get_total_classes_by_subject(subject_id)
        student_stats_rows = AttendanceRepository.get_student_stats_by_subject(subject_id)

        student_stats = []
        for row in student_stats_rows:
            name = row["student_name"]
            count = row["attended_count"]
            percentage = (count / total_classes * 100) if total_classes > 0 else 0
            student_stats.append({
                "name": name,
                "attended": count,
                "total": total_classes,
                "percentage": round(percentage, 1)
            })
        
        return records, student_stats

    @staticmethod
    def gen_frames(subject_id):
        cap = cv2.VideoCapture(0)
        marked = set()
        FACE_SIZE = (200, 200)
        CONF_THRESHOLD = 95.0

        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return

        while True:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            if face_cascade:
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=3, minSize=(80, 80)
                )

                for (x, y, w, h) in faces:
                    face_roi = gray[y:y + h, x:x + w]
                    if face_roi.size == 0: continue
                    
                    face_roi = cv2.resize(face_roi, FACE_SIZE)
                    
                    name = "Unknown"
                    confidence = 100.0
                    
                    if recognizer:
                        label_id, confidence = recognizer.predict(face_roi)
                        if confidence < CONF_THRESHOLD and 0 <= label_id < len(label_names):
                            name = label_names[label_id]
                            if name not in marked:
                                AttendanceRepository.mark_attendance(subject_id, name)
                                marked.add(name)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name} ({confidence:.1f})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret: continue

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
            
            time.sleep(0.01)
