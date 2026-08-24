"""
config.py
----------
All settings for the THDC Visitor Management website live here.
Nothing in the actual program logic (app.py / database.py) checks
usernames or passwords directly - they only read whatever is stored
in the database. This file is only used ONCE, the very first time
the app runs, to create the Head Admin account inside the database.

If you want to change the head admin's starting username/password,
change it here BEFORE running the app for the first time.
After the first run, the head admin can add/remove other admins
from the website itself - no code editing needed for that.
"""

# Database file
DATABASE_NAME = "thdc_visitor.db"

# Head Admin - created only once, on first run, if it does not exist
HEAD_ADMIN_USERNAME = "Anirudh"
HEAD_ADMIN_PASSWORD = "Anirudh@123"

# Flask secret key (used to keep login sessions secure)
SECRET_KEY = "thdc-visitor-management-secret-key"

# ---------------- OTP settings ----------------
OTP_LENGTH = 6              # how many digits in each OTP
OTP_EXPIRY_MINUTES = 5      # how long an OTP stays valid

# ---------------- Email (SMTP) settings ----------------
# Used to send the "THDC Visitor Pass" email after OTP verification.
# Fill these with a real mail account before running the app.
# For Gmail: turn on 2-Step Verification, then create an
# "App Password" - use THAT here, not your normal Gmail password.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "thdcvisitorpass@gmail.com"
SMTP_PASSWORD = "saqswjyiijnyorjm"

# ---------------- SMS settings (2Factor.in) ----------------
# Real OTP SMS is sent via 2Factor.in's Custom OTP SMS API.
# Get/regenerate this key from your 2Factor.in dashboard.
TWO_FACTOR_API_KEY = "0c0ec813-9cab-11f1-9cb1-0200cd936042"

