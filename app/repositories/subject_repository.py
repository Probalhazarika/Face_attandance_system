from app import get_db_connection

class SubjectRepository:
    @staticmethod
    def create_subject(teacher_id, subject_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO subjects (teacher_id, subject_name) VALUES (?, ?)",
            (teacher_id, subject_name)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_subjects_by_teacher_id(teacher_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, subject_name as name FROM subjects WHERE teacher_id = ?",
            (teacher_id,)
        )
        subjects = [dict(row) for row in cur.fetchall()]
        conn.close()
        return subjects

    @staticmethod
    def get_all_subjects():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, teacher_id, subject_name as name FROM subjects")
        subjects = [dict(row) for row in cur.fetchall()]
        conn.close()
        return subjects

    @staticmethod
    def delete_subject(subject_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
