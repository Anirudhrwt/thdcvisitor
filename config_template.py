"""
config_template.py
---------------------
This is the file that gets uploaded to GitHub - it has placeholder
values only, no real passwords or API keys.

HOW TO USE THIS FILE:
1. Make a copy of this file and rename the copy to "config.py"
2. Fill in your own real values in that copy
   (head admin credentials, SMTP email/password, SMS API key)
3. config.py is listed in .gitignore, so your real secrets never
   get pushed to GitHub, even if you commit and push everything else

All settings for the THDC Visitor Management website live here.
Nothing in the actual program logic (app.py / database.py) checks
usernames or passwords directly - they only read whatever is stored
in the database. The HEAD_ADMIN_* values are only used ONCE, the
very first time the app runs, to create the Head Admin account
inside the database.
"""

# Database file
DATABASE_NAME = "thdc_visitor.db"

# Head Admin - created only once, on first run, if it does not exist
HEAD_ADMIN_USERNAME = "your-head-admin-username"
HEAD_ADMIN_PASSWORD = "your-head-admin-password"

# Flask secret key (used to keep login sessions secure) - use any
# long random string; changing it logs everyone out on next restart
SECRET_KEY = "replace-this-with-a-long-random-string"

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
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-16-character-app-password"

# ---------------- SMS settings (2Factor.in) ----------------
# Real OTP SMS is sent via 2Factor.in's Custom OTP SMS API.
# Get this key from your 2Factor.in dashboard.
TWO_FACTOR_API_KEY = "your-2factor-api-key"
