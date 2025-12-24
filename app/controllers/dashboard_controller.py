from flask import render_template, session, redirect, url_for, request, flash
from app.services.dashboard_service import DashboardService
from datetime import datetime

class DashboardController:
    @staticmethod
    def dashboard():
        if "teacher_id" not in session:
            return redirect(url_for("auth.login"))

        teacher_id = session["teacher_id"]
        teacher_name, subjects = DashboardService.get_teacher_dashboard(teacher_id)

        return render_template(
            "dashboard.html",
            teacher_name=teacher_name,
            subjects=subjects,
            now=datetime.now()
        )

    @staticmethod
    def add_subject():
        if "teacher_id" not in session:
            return redirect(url_for("auth.login"))
            
        if request.method == "POST":
            subject_name = request.form.get("subject_name")
            teacher_id = session["teacher_id"]
            
            if not subject_name:
                flash("Subject name is required", "error")
            else:
                success, msg = DashboardService.add_subject(teacher_id, subject_name)
                flash(msg, "success" if success else "error")
                
        return redirect(url_for("dashboard.dashboard"))
