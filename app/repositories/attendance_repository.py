from app import get_db_connection
import sqlite3
from datetime import datetime

class AttendanceRepository:
    @staticmethod
    def mark_attendance(subject_id, student_name):
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")

        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Check if already marked
            cur.execute(
                "SELECT 1 FROM attendance WHERE subject_id = ? AND student_name = ? AND date = ?",
                (subject_id, student_name, today)
            )
            if cur.fetchone():
                print(f"[INFO] {student_name} already marked for Subject ID {subject_id} today.")
                return False

            cur.execute(
                "INSERT INTO attendance (subject_id, student_name, date, time) VALUES (?, ?, ?, ?)",
                (subject_id, student_name, today, now_time)
            )
            conn.commit()
            print(f"[ATTENDANCE] Marked {student_name} for Subject ID {subject_id} at {now_time}")
            return True
        except sqlite3.Error as e:
            print(f"[ERROR] Database error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_records_by_subject(subject_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT student_name as Name, date || ' ' || time as DateTime FROM attendance WHERE subject_id = ? ORDER BY date DESC, time DESC",
            (subject_id,)
        )
        records = cur.fetchall()
        conn.close()
        return records

    @staticmethod
    def get_total_classes_by_subject(subject_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT date) FROM attendance WHERE subject_id = ?", (subject_id,))
        total_classes = cur.fetchone()[0]
        conn.close()
        return total_classes

    @staticmethod
    def get_student_stats_by_subject(subject_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT student_name, COUNT(*) as attended_count
            FROM attendance
            WHERE subject_id = ?
            GROUP BY student_name
        """, (subject_id,))
        stats = cur.fetchall()
        conn.close()
        return stats
