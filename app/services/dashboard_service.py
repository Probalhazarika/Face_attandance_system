from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.repositories.attendance_repository import AttendanceRepository

class DashboardService:
    @staticmethod
    def get_teacher_dashboard(teacher_id):
        teacher = UserRepository.get_teacher_by_id(teacher_id)
        teacher_name = teacher["name"] if teacher else "Teacher"
        subjects = SubjectRepository.get_subjects_by_teacher_id(teacher_id)
        return teacher_name, subjects

    @staticmethod
    def add_subject(teacher_id, subject_name):
        try:
            SubjectRepository.create_subject(teacher_id, subject_name)
            return True, "Subject added successfully"
        except Exception as e:
            return False, f"Error adding subject: {e}"

    @staticmethod
    def get_admin_dashboard():
        teachers = UserRepository.get_all_teachers()
        teachers_data = []
        
        for t in teachers:
            t_data = t.copy()
            subjects = SubjectRepository.get_subjects_by_teacher_id(t["id"])
            
            # Enrich subjects with attendance records
            for s in subjects:
                s["attendance"] = AttendanceRepository.get_records_by_subject(s["id"])
            
            t_data["subjects"] = subjects
            teachers_data.append(t_data)
            
        return teachers_data
