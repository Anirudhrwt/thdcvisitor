"""
auth_routes.py
------------------
Login and logout for admins and the head admin:

    /admin      -> Login page
    /logout     -> Logout

No usernames/passwords are written directly in this file - it only
ever asks database.py to check credentials, which reads from the
database. This keeps the logic reusable and not hardcoded.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

import database

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/admin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = database.check_login(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            database.update_last_login(username)
            database.log_login(username, user["role"])
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
