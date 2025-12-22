from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository

class AuthService:
    @staticmethod
    def login_teacher(email, password):
        teacher = UserRepository.get_teacher_by_email(email)
        if teacher and check_password_hash(teacher["password"], password):
            return teacher
        return None

    @staticmethod
    def register_teacher(name, email, password, subjects_list):
        hashed = generate_password_hash(password)
        teacher_id = UserRepository.create_teacher(name, email, hashed)
        
        if teacher_id:
            for subj in subjects_list:
                SubjectRepository.create_subject(teacher_id, subj)
            return True
        return False

    @staticmethod
    def login_admin(email, password):
        admin = UserRepository.get_admin_by_email(email)
        if admin and check_password_hash(admin["password"], password):
            return admin
        return None

    @staticmethod
    def register_admin(name, email, password):
        # Check if admin already exists
        if UserRepository.count_admins() > 0:
            return False, "Access Denied: An administrator account already exists. Only one admin is allowed."

        hashed = generate_password_hash(password)
        success = UserRepository.create_admin(name, email, hashed)
        if success:
            return True, "Success"
        return False, "Email already registered"
