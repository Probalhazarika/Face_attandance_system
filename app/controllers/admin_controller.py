from flask import render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService

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

        teachers_data = DashboardService.get_admin_dashboard()
        return render_template("admin_dashboard.html", admin_name=session["admin_name"], teachers_data=teachers_data)
