"""
email_service.py
-------------------
Sends the "THDC Visitor Pass" email once a visitor's mobile
number has been OTP-verified. Uses Python's built-in smtplib,
so no extra library needs to be installed.

The email is styled like an ID / boarding-pass card (navy and
gold accents) rather than a plain message. It's built with an
HTML <table> layout and inline styles because that is what
actually renders consistently across email apps (Gmail, Outlook,
Apple Mail, etc.) - modern CSS like flexbox or grid is stripped
out by most of them.

Requires SMTP_EMAIL and SMTP_PASSWORD to be set in config.py.
For Gmail, use an "App Password" (not your normal password) -
Gmail blocks normal-password logins from scripts.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import config


def send_visitor_pass(to_email, name, reason, visit_time, pass_id):
    """visit_time is stored as 'YYYY-MM-DD HH:MM:SS' - split it so the
    email can show date and time separately, in small text. pass_id is
    the same one already saved against this visitor in the database."""
    date_part, time_part = visit_time.split(" ")

    html_body = f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background:#eef1f6; padding:40px 0; font-family:Arial, Helvetica, sans-serif;">
      <tr>
        <td align="center">
          <table role="presentation" width="440" cellpadding="0" cellspacing="0"
                 style="background:#ffffff; border-radius:14px; overflow:hidden;
                        box-shadow:0 10px 30px rgba(15,23,42,0.15);">

            <!-- Header -->
            <tr>
              <td style="background-color:#0f172a; background:linear-gradient(135deg,#0f172a,#1e3a8a); padding:24px 30px;" align="center">
                <div style="color:#ffffff; font-size:22px; font-weight:bold; letter-spacing:0.5px;">
                  THDC VISITOR PASS
                </div>
              </td>
            </tr>

            <!-- Gold divider -->
            <tr><td style="height:4px; background:linear-gradient(90deg,#d4af37,#f5e7a3,#d4af37);"></td></tr>

            <!-- Visitor Name -->
            <tr>
              <td style="padding:30px 30px 6px;" align="center">
                <div style="font-size:11px; color:#9ca3af; letter-spacing:2px; margin-bottom:6px;">VISITOR NAME</div>
                <div style="font-size:26px; font-weight:bold; color:#0f172a;">{name}</div>
              </td>
            </tr>

            <!-- Reason to visit -->
            <tr>
              <td style="padding:6px 30px 20px;" align="center">
                <div style="font-size:11px; color:#9ca3af; letter-spacing:2px; margin-bottom:4px;">REASON TO VISIT</div>
                <div style="font-size:14px; color:#374151;">{reason}</div>
              </td>
            </tr>

            <!-- Dashed ticket-style divider -->
            <tr>
              <td style="padding:0 30px;">
                <div style="border-top:2px dashed #d1d5db;"></div>
              </td>
            </tr>

            <!-- Pass ID -->
            <tr>
              <td style="padding:20px 30px;" align="center">
                <div style="font-size:12px; color:#6b7280; letter-spacing:1px;">
                  PASS ID: <span style="color:#0f172a; font-weight:bold;">{pass_id}</span>
                </div>
              </td>
            </tr>

            <!-- Date & Time (small, as requested) -->
            <tr>
              <td style="padding:0 30px 26px;" align="center">
                <div style="font-size:11px; color:#9ca3af;">
                  Date: {date_part} &nbsp;|&nbsp; Time: {time_part}
                </div>
              </td>
            </tr>

            <!-- Footer strip -->
            <tr>
              <td style="background:#0f172a; padding:14px; text-align:center;">
                <div style="color:#94a3b8; font-size:11px; letter-spacing:1px;">
                  Please carry this pass and a valid ID at the security gate.
                </div>
              </td>
            </tr>

          </table>
        </td>
      </tr>
    </table>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your THDC Visitor Pass"
    msg["From"] = config.SMTP_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_EMAIL, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Could not send visitor pass: {e}")
        return False
