from flask import render_template, session, redirect, url_for
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
