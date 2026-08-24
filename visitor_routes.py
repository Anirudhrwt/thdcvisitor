"""
visitor_routes.py
--------------------
Everything a VISITOR (not an admin) interacts with:

    /               -> THDC Visitor Form
    /verify-otp     -> Enter the OTP sent to their mobile number
    /resend-otp     -> Send a fresh OTP to the same mobile number

Kept in its own Blueprint, separate from the admin/login/dashboard
routes, since visitors and admins never touch each other's pages.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

import database
import otp_service
import sms_service
import email_service

visitor_bp = Blueprint("visitor", __name__)


# ---------------- Visitor Form (public page) ----------------

@visitor_bp.route("/", methods=["GET", "POST"])
def visitor_form():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        reason = request.form.get("reason", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not (name and reason and email and phone):
            flash("Please fill all the fields.")
            return redirect(url_for("visitor.visitor_form"))

        if not (phone.isdigit() and len(phone) == 10):
            flash("Mobile number must be exactly 10 digits.")
            return redirect(url_for("visitor.visitor_form"))

        # Details are held as "pending" until the mobile number is OTP-verified
        otp = otp_service.generate_otp()
        expires_at = otp_service.get_expiry_time()
        database.save_pending_visitor(name, reason, email, phone, otp, expires_at)
        sms_service.send_otp_sms(phone, otp)

        session["pending_phone"] = phone
        flash("An OTP has been sent to your mobile number.")
        return redirect(url_for("visitor.verify_otp"))

    return render_template("visitor_form.html")


# ---------------- OTP Verification ----------------

@visitor_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    phone = session.get("pending_phone")
    if not phone:
        return redirect(url_for("visitor.visitor_form"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        pending = database.get_pending_visitor(phone)

        if pending is None:
            flash("No pending verification found. Please fill the form again.")
            session.pop("pending_phone", None)
            return redirect(url_for("visitor.visitor_form"))

        if otp_service.is_expired(pending["expires_at"]):
            flash("OTP expired. Please request a new one.")
            return redirect(url_for("visitor.verify_otp"))

        if entered_otp != pending["otp"]:
            flash("Incorrect OTP. Please try again.")
            return redirect(url_for("visitor.verify_otp"))

        # OTP correct -> save as a real visitor and send the pass by email
        visitor_id, visit_time, pass_id = database.add_visitor(
            pending["name"], pending["reason"], pending["email"], phone
        )
        database.delete_pending_visitor(phone)
        session.pop("pending_phone", None)

        email_service.send_visitor_pass(
            pending["email"], pending["name"], pending["reason"], visit_time, pass_id
        )
        flash("Mobile number verified! Your THDC Visitor Pass has been emailed to you.")
        return redirect(url_for("visitor.visitor_form"))

    return render_template("otp_verify.html", phone=phone)


@visitor_bp.route("/resend-otp")
def resend_otp():
    phone = session.get("pending_phone")
    if not phone:
        return redirect(url_for("visitor.visitor_form"))

    pending = database.get_pending_visitor(phone)
    if pending is None:
        return redirect(url_for("visitor.visitor_form"))

    otp = otp_service.generate_otp()
    expires_at = otp_service.get_expiry_time()
    database.save_pending_visitor(
        pending["name"], pending["reason"], pending["email"], phone, otp, expires_at
    )
    sms_service.send_otp_sms(phone, otp)
    flash("A new OTP has been sent to your mobile number.")
    return redirect(url_for("visitor.verify_otp"))
