from app import get_db_connection
import sqlite3

class UserRepository:
    @staticmethod
    def get_teacher_by_email(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM teachers WHERE email = ?", (email,))
        teacher = cur.fetchone()
        conn.close()
        return teacher

    @staticmethod
    def create_teacher(name, email, password_hash):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO teachers (name, email, password) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            teacher_id = cur.lastrowid
            conn.commit()
            return teacher_id
        except sqlite3.IntegrityError:
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_teacher_by_id(teacher_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM teachers WHERE id = ?", (teacher_id,))
        teacher = cur.fetchone()
        conn.close()
        return teacher

    @staticmethod
    def get_all_teachers():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM teachers")
        teachers = [dict(row) for row in cur.fetchall()]
        conn.close()
        return teachers

    @staticmethod
    def count_admins():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM admins")
        count = cur.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def create_admin(name, email, password_hash):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO admins (name, email, password) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_admin_by_email(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admins WHERE email = ?", (email,))
        admin = cur.fetchone()
        conn.close()
        return admin
