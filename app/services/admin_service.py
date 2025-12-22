from app import get_db_connection
import sqlite3

class AdminService:
    # -----------------------------
    # TEACHER MANAGEMENT
    # -----------------------------
    @staticmethod
    def get_all_teachers():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM teachers")
        teachers = cur.fetchall()
        conn.close()
        return teachers

    @staticmethod
    def add_teacher(name, email, password):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO teachers (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            return True, "Teacher added successfully"
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        finally:
            conn.close()

    @staticmethod
    def update_teacher(teacher_id, name, email):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE teachers SET name = ?, email = ? WHERE id = ?", (name, email, teacher_id))
            conn.commit()
            return True, "Teacher updated successfully"
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        finally:
            conn.close()

    @staticmethod
    def delete_teacher(teacher_id):
        conn = get_db_connection()
        cur = conn.cursor()
        # Dependencies in subjects/attendance will cascade if foreign keys enabled, else manual cleanup needed
        # Simple deletion for now
        cur.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        conn.commit()
        conn.close()
        return True, "Teacher deleted"

    # -----------------------------
    # STUDENT MANAGEMENT
    # -----------------------------
    @staticmethod
    def get_all_students():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        conn.close()
        return students

    @staticmethod
    def add_student(name, roll_number, email):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO students (name, roll_number, email) VALUES (?, ?, ?)", 
                        (name, roll_number, email))
            conn.commit()
            return True, "Student added successfully"
        except sqlite3.IntegrityError:
            return False, "Roll number already exists"
        finally:
            conn.close()

    @staticmethod
    def update_student(student_id, name, roll_number, email):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE students SET name = ?, roll_number = ?, email = ? WHERE id = ?", 
                        (name, roll_number, email, student_id))
            conn.commit()
            return True, "Student updated successfully"
        except sqlite3.IntegrityError:
            return False, "Roll number already exists"
        finally:
            conn.close()

    @staticmethod
    def delete_student(student_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return True, "Student deleted"

    # -----------------------------
    # ATTENDANCE MANAGEMENT
    # -----------------------------
    @staticmethod
    def get_all_attendance():
        conn = get_db_connection()
        cur = conn.cursor()
        # Joining to get subject names
        query = """
            SELECT a.id, a.student_name, a.date, a.time, s.subject_name, t.name as teacher_name
            FROM attendance a
            JOIN subjects s ON a.subject_id = s.id
            JOIN teachers t ON s.teacher_id = t.id
            ORDER BY a.date DESC, a.time DESC
        """
        cur.execute(query)
        records = cur.fetchall()
        conn.close()
        return records

    @staticmethod
    def update_attendance(record_id, student_name, date, time):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE attendance SET student_name = ?, date = ?, time = ? WHERE id = ?", 
                        (student_name, date, time, record_id))
            conn.commit()
            return True, "Attendance record updated"
        except sqlite3.Error as e:
            return False, f"Error: {e}"
        finally:
            conn.close()

    @staticmethod
    def delete_attendance(record_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True, "Attendance record deleted"
