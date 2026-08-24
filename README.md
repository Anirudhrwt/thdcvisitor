# THDC Visitor Management

A visitor management system for THDC, built with **Python (Flask) + HTML + CSS**.
Visitors check in through a form, verify their mobile number with an OTP, and
get a digital Visitor Pass emailed to them automatically. Admins log in to a
unified dashboard to view visitor records, and the Head Admin can add/remove
other admins and monitor everyone's login activity.

## Features

- 📝 **Visitor Form** — Name, Mobile Number, Email, Reason to Visit
- 📲 **OTP mobile verification** — via 2Factor.in, before a visit is recorded
- 🎫 **Automatic Visitor Pass email** — a styled pass with a unique Pass ID,
  emailed the moment OTP verification succeeds
- 🔐 **Role-based admin access** — Head Admin vs regular Admins
- 🛡️ **Head Admin controls** — add/remove admins, view every admin's login
  history (and their own) in one place
- 📊 **Unified sidebar dashboard** — Visitor Details, Manage Admins, and
  Login Activity all on one page, switching tabs with no reload
- 🗄️ **SQLite database** — no external database server needed

## Folder Structure (every part in its own file)

```
thdc_visitor_management/
├── app.py                  # Entry point: creates the app, wires everything together
├── visitor_routes.py       # Visitor form + OTP verification routes
├── auth_routes.py          # Login / logout routes
├── dashboard_routes.py     # Unified admin dashboard + manage-admins routes
├── auth_helpers.py         # Shared "is logged in?" / "is head admin?" checks
├── database.py             # All database operations
├── config_template.py      # Placeholder settings file (safe to commit)
├── config.py                # Your real settings - NOT committed, see Setup below
├── otp_service.py           # OTP generation + expiry rules
├── sms_service.py           # Sends the OTP via 2Factor.in
├── email_service.py         # Sends the THDC Visitor Pass email
├── requirements.txt         # Python dependencies
├── .gitignore                # Keeps config.py and the database out of git
├── LICENSE                   # MIT License
├── index.html                 # Static landing page for GitHub Pages (see note below)
├── static/
│   └── style.css             # Shared styling
└── templates/
    ├── visitor_form.html    # Public "THDC Visitor Form" page
    ├── otp_verify.html      # Enter the OTP page
    ├── login.html           # Admin login page
    └── dashboard.html       # Unified dashboard (sidebar + tabs, all sections)
```

Routes are split using Flask **Blueprints** — each feature area
(visitor-facing pages, login, admin dashboard) registers its own routes
from its own file, and `app.py` just creates the app and plugs them all
in. Every file has exactly one job.

> **Note on `index.html`:** the real app doesn't use this file — the
> live homepage is served dynamically by Flask (`visitor_routes.py` +
> `templates/visitor_form.html`). `index.html` at the repo root is only
> there so **GitHub Pages** has something to show if you ever enable it
> for this repo (Pages can only serve static files, not run Python).

## How it works

1. **Visitor Form (`/`)** — Visitor fills in Name, Mobile Number, Email,
   Reason to Visit and submits.

2. **OTP Verification (`/verify-otp`)** — A 6-digit OTP is generated and
   sent to the mobile number via 2Factor.in. The visit is **not** saved
   to the database until the correct OTP is entered. OTPs expire after
   5 minutes (configurable) and can be resent.

3. **On correct OTP** — The visitor is saved to the database with the
   **date & time recorded automatically** and a unique **Pass ID**
   (e.g. `THDC-00007`). A **THDC Visitor Pass** email is sent to the
   address they gave, showing their **Name**, **Reason to Visit**,
   **Pass ID**, and **Date & Time** (in small text).

4. **Admin Login (`/admin`)** — Admins and the Head Admin log in here.
   The first time the app runs, a Head Admin account is created
   automatically using the credentials in `config.py`. Nothing is
   hardcoded in the program logic — routes only ever check whatever is
   stored in the database, so more admins can be added later from the
   website itself.

5. **Dashboard (`/dashboard`)** — One unified page with a sidebar:
   - **Visitor Details** — visible to every logged-in admin
   - **Manage Admins** — head admin only: add/remove admins
   - **Login Activity** — head admin only: every login by every account,
     most recent first

   All three sections load together — clicking a sidebar tab just shows
   that section instantly, no page reload. Regular admins only see the
   Visitor Details tab.

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd thdc_visitor_management
pip install -r requirements.txt
```

### 2. Create your local config file

`config.py` holds real credentials, so it's excluded from this repo via
`.gitignore`. Create your own copy from the template:

```bash
cp config_template.py config.py
```

Then open `config.py` and fill in:

- **Head Admin username/password** — created automatically on first run
- **`SECRET_KEY`** — any long random string
- **SMTP_EMAIL / SMTP_PASSWORD** — a Gmail address + an **App Password**
  (Google Account → Security → turn on 2-Step Verification → App
  Passwords). Your normal Gmail password will not work.
- **TWO_FACTOR_API_KEY** — from your [2factor.in](https://2factor.in)
  dashboard, used to send real OTP SMS

### 3. Run it

```bash
python app.py
```

Open `http://127.0.0.1:5000/` in your browser.

A file named `thdc_visitor.db` (SQLite) is created automatically on
first run — that's where visitors, pending OTPs, and admin accounts are
stored. It's also excluded from git.

## Notes

- Passwords are stored as hashes (not plain text) using Werkzeug's
  `generate_password_hash`.
- If `sms_service.py` or `email_service.py` can't reach their provider
  (no internet, wrong credentials, etc.), the OTP is printed to the
  terminal as a fallback so the flow never gets fully blocked during
  testing.
- To change the head admin's password later, either add a "change
  password" feature, or delete `thdc_visitor.db` and update `config.py`
  before running again (this resets visitor data too).

## License

MIT — see [LICENSE](LICENSE).
