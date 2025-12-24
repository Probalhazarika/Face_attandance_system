from flask import Blueprint
from app.controllers.admin_controller import AdminController

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/register", methods=["GET", "POST"])
def register():
    return AdminController.register()

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    return AdminController.login()

@admin_bp.route("/dashboard")
def dashboard():
    return AdminController.dashboard()

# Teachers
@admin_bp.route("/teacher/add", methods=["POST"])
def add_teacher():
    return AdminController.add_teacher()

@admin_bp.route("/teacher/edit/<int:teacher_id>", methods=["POST"])
def edit_teacher(teacher_id):
    return AdminController.edit_teacher(teacher_id)

@admin_bp.route("/teacher/delete/<int:teacher_id>")
def delete_teacher(teacher_id):
    return AdminController.delete_teacher(teacher_id)

@admin_bp.route("/teacher/subject/add/<int:teacher_id>", methods=["POST"])
def add_subject(teacher_id):
    return AdminController.add_subject(teacher_id)

@admin_bp.route("/teacher/subject/delete/<int:subject_id>")
def delete_subject(subject_id):
    return AdminController.delete_subject(subject_id)

# Students
@admin_bp.route("/student/add", methods=["POST"])
def add_student():
    return AdminController.add_student()

@admin_bp.route("/student/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    return AdminController.edit_student(student_id)

@admin_bp.route("/student/delete/<int:student_id>")
def delete_student(student_id):
    return AdminController.delete_student(student_id)

# Attendance
@admin_bp.route("/attendance/edit/<int:record_id>", methods=["POST"])
def edit_attendance(record_id):
    return AdminController.edit_attendance(record_id)

@admin_bp.route("/attendance/delete/<int:record_id>")
def delete_attendance(record_id):
    return AdminController.delete_attendance(record_id)
