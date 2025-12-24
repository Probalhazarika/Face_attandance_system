from flask import Blueprint
from app.controllers.dashboard_controller import DashboardController

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    return DashboardController.dashboard()

@dashboard_bp.route("/dashboard/subject/add", methods=["POST"])
def add_subject():
    return DashboardController.add_subject()
