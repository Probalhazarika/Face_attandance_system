import cv2
import os
import pickle
import time
import numpy as np
from app.repositories.attendance_repository import AttendanceRepository

# Try to import face_recognition and sklearn
try:
    import face_recognition
except ImportError:
    face_recognition = None
    print("[ERROR] 'face_recognition' library not found. Install it via pip.")

# Load Model Global
MODEL_PATH = "model/recognizer.pickle"
LE_PATH = "model/le.pickle"

recognizer = None
le = None

def load_model():
    global recognizer, le
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LE_PATH):
        print(f"[WARN] SVM Model not found at {MODEL_PATH}. Run 'train_classifier.py' first.")
        return

    try:
        recognizer = pickle.loads(open(MODEL_PATH, "rb").read())
        le = pickle.loads(open(LE_PATH, "rb").read())
        print("[INFO] Loaded Transformer-based Face Recognition Model (SVM Classifier).")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")

# Initialize on import
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
        
        # Hyperparameters for Research/Tuning
        CONF_THRESHOLD = 0.60  # 60% Confidence required
        
        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return

        if face_recognition is None:
            print("[ERROR] Library missing. Cannot run.")
            return

        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # Resize for faster processing (optional, but 0.25 is standard for speed)
            # However, for accuracy in a major project, we might keep it or use 0.5
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            
            # Convert BGR (OpenCV) to RGB (face_recognition)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # 1. Detect Faces (HOG method)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            
            # 2. Extract Embeddings (128-d vectors)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_data = []
            
            for face_encoding in face_encodings:
                name = "Unknown"
                confidence = 0.0
                
                if recognizer and le:
                    # Check for KNN-style distance support
                    if hasattr(recognizer, "kneighbors"):
                        # KNN Logic: Use Euclidean distance
                        # distance 0.0 = perfect match, > 0.6 = likely unknown
                        dist_list, _ = recognizer.kneighbors([face_encoding], n_neighbors=1, return_distance=True)
                        distance = dist_list[0][0]
                        
                        # Convert to "confidence" for display (1.0 - distance)
                        confidence = 1.0 - distance
                        
                        # Thresholding: 0.50 as requested by user
                        if distance < 0.50:
                            # Valid match
                            pred_idx = recognizer.predict([face_encoding])[0]
                            name = le.inverse_transform([pred_idx])[0]
                            
                            if name not in marked:
                                AttendanceRepository.mark_attendance(subject_id, name)
                                marked.add(name)
                        else:
                            name = "Unknown"
                            
                    else:
                        # SVM / Probability Logic
                        # reshape to (1, 128)
                        preds = recognizer.predict_proba([face_encoding])[0]
                        j = np.argmax(preds)
                        confidence = preds[j]
                        
                        # 4. Manual Thresholding
                        if confidence > CONF_THRESHOLD:
                            name = le.classes_[j]
                            if name not in marked:
                                AttendanceRepository.mark_attendance(subject_id, name)
                                marked.add(name)
                
                face_data.append((name, confidence))

                # Display results
            for (top, right, bottom, left), (name, confidence) in zip(face_locations, face_data):
                # Scale back up
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2

                # Calculate "Uncertainty" or "Distance-like" metric
                # confidence is 0..1 (higher is better)
                # val is 0..1 (higher is worse)
                val = 1.0 - confidence

                # Draw box
                color = (0, 255, 0) if "Unknown" not in name else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw Name above
                y_name = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y_name), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                # Draw Metric below the box
                # Format: "Diff: 0.25"
                text_val = f"Diff: {val:.2f}"
                cv2.putText(frame, text_val, (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.60, color, 2)

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret: continue

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
            
            time.sleep(0.01)

