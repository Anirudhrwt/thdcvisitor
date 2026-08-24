"""
otp_service.py
-----------------
Small helper file just for OTP rules:
- generating a random OTP
- working out when it should expire
- checking if an OTP has expired

Storing the OTP and actually sending it are handled by
database.py and sms_service.py.
"""

import random
from datetime import datetime, timedelta

import config


def generate_otp():
    digits = "0123456789"
    return "".join(random.choice(digits) for _ in range(config.OTP_LENGTH))


def get_expiry_time():
    expiry = datetime.now() + timedelta(minutes=config.OTP_EXPIRY_MINUTES)
    return expiry.strftime("%Y-%m-%d %H:%M:%S")


def is_expired(expires_at):
    return datetime.now() > datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
