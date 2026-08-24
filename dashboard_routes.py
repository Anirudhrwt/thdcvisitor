"""
dashboard_routes.py
----------------------
The logged-in admin area:

    /dashboard        -> One unified dashboard (Visitor Details always;
                          Manage Admins + Login Activity tabs added for
                          the head admin) - all sections load together,
                          switching tabs never reloads the page.
    /manage-admins    -> Handles the add/remove admin form, then
                          returns to the dashboard's Manage Admins tab
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

import database
from auth_helpers import is_logged_in, is_head_admin

dashboard_bp = Blueprint("dashboard", __name__)


# ---------------- Unified Dashboard ----------------
# Visitor Details is always included. Manage Admins and Login Activity
# data is only fetched and included for the head admin. All of it is
# rendered together in one page - the sidebar tabs just show/hide
# sections client-side, nothing needs to reload.

@dashboard_bp.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    role = session.get("role")
    visitors = database.get_all_visitors()
    admins = database.get_all_admins() if role == "head_admin" else None
    login_logs = database.get_all_login_logs() if role == "head_admin" else None
    active_tab = request.args.get("tab", "visitors")

    return render_template(
        "dashboard.html",
        visitors=visitors,
        admins=admins,
        login_logs=login_logs,
        username=session.get("username"),
        role=role,
        active_tab=active_tab,
    )


# ---------------- Manage Admins form handler (head admin only) ----------------

@dashboard_bp.route("/manage-admins", methods=["POST"])
def manage_admins():
    if not is_logged_in():
        return redirect(url_for("auth.login"))
    if not is_head_admin():
        flash("Only the head admin can access this page.")
        return redirect(url_for("dashboard.dashboard"))

    action = request.form.get("action")

    if action == "add":
        new_username = request.form.get("username", "").strip()
        new_password = request.form.get("password", "").strip()
        if new_username and new_password:
            added = database.add_admin(new_username, new_password)
            if added:
                flash(f"Admin '{new_username}' added successfully.")
            else:
                flash(f"Username '{new_username}' already exists.")
        else:
            flash("Please provide both username and password.")

    elif action == "remove":
        admin_id = request.form.get("admin_id")
        database.remove_admin(admin_id)
        flash("Admin removed successfully.")

    return redirect(url_for("dashboard.dashboard", tab="manage"))
