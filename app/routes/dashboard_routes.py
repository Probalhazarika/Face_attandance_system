from flask import Blueprint
from app.controllers.dashboard_controller import DashboardController

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    return DashboardController.dashboard()
