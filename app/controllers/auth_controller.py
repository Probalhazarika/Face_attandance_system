from flask import render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService

class AuthController:
    @staticmethod
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            
            teacher = AuthService.login_teacher(email, password)
            if teacher:
                session["teacher_id"] = teacher["id"]
                session["teacher_name"] = teacher["name"]
                flash("Login successful!", "success")
                return redirect(url_for("dashboard.dashboard"))
            else:
                flash("Invalid email or password", "error")
                return render_template("login.html")
        return render_template("login.html")

    @staticmethod
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            subjects_raw = request.form.get("subjects", "")

            if not name or not email or not password:
                flash("Name, email and password are required.", "error")
                return render_template("register.html")

            subjects = [s.strip() for s in subjects_raw.split(",") if s.strip()]
            success = AuthService.register_teacher(name, email, password, subjects)
            
            if success:
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("Email already registered. Please log in.", "error")
                return render_template("register.html")
        return render_template("register.html")

    @staticmethod
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("auth.login"))
