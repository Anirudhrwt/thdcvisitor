"""
auth_helpers.py
------------------
Tiny shared helpers for checking who's logged in and what role
they have. Used by dashboard_routes.py (and could be reused by
any other route file that needs to check login status).

Kept separate so route files don't need to duplicate this logic
or import each other just to share it.
"""

from flask import session


def is_logged_in():
    return "user_id" in session


def is_head_admin():
    return session.get("role") == "head_admin"
