"""
sms_service.py
----------------
Handles sending the OTP to the visitor's mobile number using
2Factor.in's Custom OTP SMS API (https://2factor.in).

This uses their "custom OTP" endpoint - we generate the OTP
ourselves (see otp_service.py) and just ask 2Factor.in to deliver
it as an SMS, so the rest of the app (storing/checking the OTP)
does not need to change.

If the SMS fails to send for any reason (no internet, wrong key,
low balance, etc.), the OTP is also printed to the server console
as a backup, so testing is never fully blocked.
"""

import requests

import config

TWO_FACTOR_BASE_URL = "https://2factor.in/API/V1"


def send_otp_sms(phone, otp):
    """Sends the given OTP to the given 10-digit Indian mobile number
    via 2Factor.in. Returns True if accepted, False otherwise."""

    url = f"{TWO_FACTOR_BASE_URL}/{config.TWO_FACTOR_API_KEY}/SMS/91{phone}/{otp}"

    try:
        response = requests.get(url, timeout=20)
        print(f"[SMS DEBUG] status {response.status_code}: {response.text}")

        result = response.json()
        if result.get("Status") == "Success":
            print(f"[SMS SENT] OTP sent to {phone} via 2Factor.in.")
            return True
        else:
            print(f"[SMS FAILED] 2Factor.in says: {result}")
            print(f"[SMS FALLBACK] OTP for {phone} is: {otp}")
            return False

    except Exception as e:
        print(f"[SMS ERROR] Could not reach 2Factor.in: {e}")
        print(f"[SMS FALLBACK] OTP for {phone} is: {otp}")
        return False
