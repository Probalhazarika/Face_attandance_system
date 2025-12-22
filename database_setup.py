import sqlite3

DB_PATH = "attendance.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# -------------------------
# CREATE TEACHERS TABLE
# -------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

# -------------------------
# CREATE SUBJECTS TABLE
# -------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_name TEXT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);
""")

# -------------------------
# CREATE ATTENDANCE TABLE
# -------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    student_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,

    -- ensures 1 student = 1 attendance per subject per day
    UNIQUE(subject_id, student_name, date),

    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);
""")

# -------------------------
# CREATE ADMINS TABLE
# -------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

# -------------------------
# CREATE STUDENTS TABLE
# -------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_number TEXT UNIQUE,
    email TEXT
);
""")

conn.commit()
conn.close()

print("Database initialized successfully!")
