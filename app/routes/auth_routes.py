from flask import Blueprint, render_template, session, redirect, url_for
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    if "teacher_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("index.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return AuthController.login()

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return AuthController.register()

@auth_bp.route("/logout")
def logout():
    return AuthController.logout()
