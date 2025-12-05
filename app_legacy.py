from flask import (
    Flask, render_template, Response,
    request, redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import numpy as np
import pickle
import pickle
from datetime import datetime
import os
import time
import pandas as pd
import sqlite3

# ---------------- BASIC APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "change_this_secret_key_later"

DB_PATH = "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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


def mark_attendance(name: str, subject_id: int):
    """Mark attendance in the SQLite DB for a specific subject."""
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO attendance (subject_id, student_name, date, time) VALUES (?, ?, ?, ?)",
            (subject_id, name, today, now_time)
        )
        conn.commit()
        print(f"[ATTENDANCE] Marked {name} for Subject ID {subject_id} at {now_time}")
    except sqlite3.IntegrityError:
        # Already marked for this subject today
        print(f"[INFO] {name} already marked for Subject ID {subject_id} today.")
    finally:
        conn.close()


# ---------------- FACE DETECTOR (HAAR) ----------------
haar_path = cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
face_cascade = cv2.CascadeClassifier(haar_path)
if face_cascade.empty():
    print("[WARN] Could not load Haar Cascade:", haar_path)

FACE_SIZE = (200, 200)
CONF_THRESHOLD = 95.0  # LBPH confidence; lower = better


# ---------------- VIDEO + RECOGNITION ----------------
# ---------------- VIDEO + RECOGNITION ----------------
def gen_frames(subject_id):
    cap = cv2.VideoCapture(0)
    marked = set()  # per-session spam limiter

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
                if name not in marked:
                    mark_attendance(name, subject_id)
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


# ---------------- AUTH + DASHBOARD ----------------
@app.route("/")
def home():
    """Root: if logged in -> dashboard, else -> login page."""
    if "teacher_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, email, password FROM teachers WHERE email = ?",
            (email,)
        )
        teacher = cur.fetchone()
        conn.close()

        # Verify password hash
        if teacher and check_password_hash(teacher["password"], password):
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["name"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        subjects_raw = request.form.get("subjects", "")

        if not name or not email or not password:
            flash("Name, email and password are required.", "error")
            return render_template("register.html")

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # insert teacher (store hashed password)
            hashed = generate_password_hash(password)
            cur.execute(
                "INSERT INTO teachers (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed)
            )
            teacher_id = cur.lastrowid

            # insert subjects
            subjects = [s.strip() for s in subjects_raw.split(",") if s.strip()]
            for subj in subjects:
                # subjects table uses column `subject_name` per DB setup
                cur.execute(
                    "INSERT INTO subjects (teacher_id, subject_name) VALUES (?, ?)",
                    (teacher_id, subj)
                )

            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            # email already exists (UNIQUE constraint)
            flash("Email already registered. Please log in.", "error")
            conn.rollback()
            return render_template("register.html")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    teacher_id = session["teacher_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
    row = cur.fetchone()
    teacher_name = row["name"] if row else "Teacher"

    # select subject_name but alias as `name` so templates continue to work
    cur.execute(
        "SELECT id, subject_name as name FROM subjects WHERE teacher_id = ?",
        (teacher_id,)
    )
    subjects = cur.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        teacher_name=teacher_name,
        subjects=subjects
    )


# ---------------- CAMERA / ATTENDANCE PAGES (PLACEHOLDERS) ----------------
@app.route("/start_attendance/<int:subject_id>")
def start_attendance(subject_id):
    """For now just show the camera page using the existing video_feed."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    # Later we will pass subject_id into DB-based attendance.
    return render_template("camera_attendance.html", subject_id=subject_id)


@app.route("/video_feed/<int:subject_id>")
def video_feed(subject_id):
    return Response(
        gen_frames(subject_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/view_records/<int:subject_id>")
def view_records(subject_id):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Get detailed records
    cur.execute(
        "SELECT student_name as Name, date || ' ' || time as DateTime FROM attendance WHERE subject_id = ? ORDER BY date DESC, time DESC",
        (subject_id,)
    )
    records = cur.fetchall()

    # 2. Calculate Total Classes (Unique Dates)
    cur.execute("SELECT COUNT(DISTINCT date) FROM attendance WHERE subject_id = ?", (subject_id,))
    total_classes = cur.fetchone()[0]

    # 3. Calculate Attendance per Student
    cur.execute("""
        SELECT student_name, COUNT(*) as attended_count
        FROM attendance
        WHERE subject_id = ?
        GROUP BY student_name
    """, (subject_id,))
    student_stats_rows = cur.fetchall()

    # Format stats
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

    conn.close()

    return render_template(
        "attendance.html",
        records=records,
        student_stats=student_stats,
        subject_id=subject_id
    )


# ---------------- ADMIN ROUTES ----------------
@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM admins")
    count = cur.fetchone()[0]
    
    if count > 0:
        conn.close()
        flash("Admin already exists. Only one admin allowed.", "error")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        hashed = generate_password_hash(password)
        try:
            cur.execute(
                "INSERT INTO admins (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed)
            )
            conn.commit()
            flash("Admin registered successfully. Please log in.", "success")
            return redirect(url_for("admin_login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
        finally:
            conn.close()
    else:
        conn.close()

    return render_template("admin_register.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, password FROM admins WHERE email = ?", (email,))
        admin = cur.fetchone()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["name"]
            # Clear teacher session if any
            session.pop("teacher_id", None)
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "error")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch all teachers
    cur.execute("SELECT id, name, email FROM teachers")
    teachers = [dict(row) for row in cur.fetchall()]

    # For each teacher, fetch subjects and attendance
    teachers_data = []
    for t in teachers:
        t_data = t.copy()
        cur.execute("SELECT id, subject_name as name FROM subjects WHERE teacher_id = ?", (t["id"],))
        subjects = [dict(row) for row in cur.fetchall()]
        
        for s in subjects:
            cur.execute("SELECT student_name, date, time FROM attendance WHERE subject_id = ?", (s["id"],))
            s["attendance"] = [dict(row) for row in cur.fetchall()]
        
        t_data["subjects"] = subjects
        teachers_data.append(t_data)

    conn.close()
    return render_template("admin_dashboard.html", admin_name=session["admin_name"], teachers_data=teachers_data)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
