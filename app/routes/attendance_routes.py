from flask import Blueprint
from app.controllers.attendance_controller import AttendanceController

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/start_attendance/<int:subject_id>")
def start_attendance(subject_id):
    return AttendanceController.start_attendance(subject_id)

@attendance_bp.route("/video_feed/<int:subject_id>")
def video_feed(subject_id):
    return AttendanceController.video_feed(subject_id)

@attendance_bp.route("/view_records/<int:subject_id>")
def view_records(subject_id):
    return AttendanceController.view_records(subject_id)
