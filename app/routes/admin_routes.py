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
