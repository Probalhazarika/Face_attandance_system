from flask import render_template, Response, session, redirect, url_for
from app.services.attendance_service import AttendanceService

class AttendanceController:
    @staticmethod
    def start_attendance(subject_id):
        if "teacher_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("camera_attendance.html", subject_id=subject_id)

    @staticmethod
    def video_feed(subject_id):
        return Response(
            AttendanceService.gen_frames(subject_id),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @staticmethod
    def view_records(subject_id):
        if "teacher_id" not in session:
            return redirect(url_for("auth.login"))

        records, student_stats = AttendanceService.get_attendance_stats(subject_id)

        return render_template(
            "attendance.html",
            records=records,
            student_stats=student_stats,
            subject_id=subject_id
        )
