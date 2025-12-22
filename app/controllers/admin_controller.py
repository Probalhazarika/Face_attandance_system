from flask import render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.admin_service import AdminService

class AdminController:
    @staticmethod
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            success, message = AuthService.register_admin(name, email, password)
            if success:
                flash("Admin registered successfully. Please log in.", "success")
                return redirect(url_for("admin.login"))
            else:
                flash(message, "error")
                return render_template("admin_register.html")
        return render_template("admin_register.html")

    @staticmethod
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            admin = AuthService.login_admin(email, password)
            if admin:
                session["admin_id"] = admin["id"]
                session["admin_name"] = admin["name"]
                session.pop("teacher_id", None)
                flash("Admin login successful!", "success")
                return redirect(url_for("admin.dashboard"))
            else:
                flash("Invalid credentials", "error")
        return render_template("admin_login.html")

    @staticmethod
    def dashboard():
        if "admin_id" not in session:
            return redirect(url_for("admin.login"))

        teachers = AdminService.get_all_teachers()
        students = AdminService.get_all_students()
        attendance_records = AdminService.get_all_attendance()
        
        # Keep old service reading for compatibility if needed, using new service primarily
        return render_template(
            "admin_dashboard.html", 
            admin_name=session["admin_name"], 
            teachers=teachers,
            students=students,
            attendance_records=attendance_records
        )

    # --- TEACHER CRUD ---
    @staticmethod
    def add_teacher():
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            success, msg = AdminService.add_teacher(name, email, password)
            flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))

    @staticmethod
    def edit_teacher(teacher_id):
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            success, msg = AdminService.update_teacher(teacher_id, name, email)
            flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))

    @staticmethod
    def delete_teacher(teacher_id):
        success, msg = AdminService.delete_teacher(teacher_id)
        flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))

    # --- STUDENT CRUD ---
    @staticmethod
    def add_student():
        if request.method == "POST":
            name = request.form.get("name")
            roll_number = request.form.get("roll_number")
            email = request.form.get("email")
            success, msg = AdminService.add_student(name, roll_number, email)
            flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))
    
    @staticmethod
    def edit_student(student_id):
        if request.method == "POST":
            name = request.form.get("name")
            roll_number = request.form.get("roll_number")
            email = request.form.get("email")
            success, msg = AdminService.update_student(student_id, name, roll_number, email)
            flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))

    @staticmethod
    def delete_student(student_id):
        success, msg = AdminService.delete_student(student_id)
        flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))

    # --- ATTENDANCE CRUD ---
    @staticmethod
    def edit_attendance(record_id):
        if request.method == "POST":
            student_name = request.form.get("student_name")
            date = request.form.get("date")
            time = request.form.get("time")
            success, msg = AdminService.update_attendance(record_id, student_name, date, time)
            flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))

    @staticmethod
    def delete_attendance(record_id):
        success, msg = AdminService.delete_attendance(record_id)
        flash(msg, "success" if success else "error")
        return redirect(url_for('admin.dashboard'))
