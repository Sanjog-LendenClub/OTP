from datetime import timedelta
from .constants import MAX_OTP_ATTEMPTS, OTP_EXPIRY_MINUTES
import secrets
import string
from .mappers import OTPMapper
from .utils import get_current_datetime

def generate_otp(length=6):
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def request_otp(mobile_number):
    current_datetime = get_current_datetime()

    otp_obj = OTPMapper.get_active_otp_by_mobile_number(mobile_number)

    if otp_obj and otp_obj.attempts >= MAX_OTP_ATTEMPTS:
        return None, 'Maximum attempts reached. Try again after 30 mins.'

    if otp_obj:
        if current_datetime >= otp_obj.timestamp + timedelta(minutes=OTP_EXPIRY_MINUTES):
            # Delete previous expired OTP and create a new one
            OTPMapper.delete_expired_otps(mobile_number)
            otp_obj = OTPMapper.create_otp(mobile_number, generate_otp(), 1)
            return otp_obj.otp, 'OTP sent successfully.'

        # Update the timestamp, reset the attempts counter, and resend the OTP
        OTPMapper.update_otp(otp_obj, generate_otp(), otp_obj.attempts + 1)
        otp_obj.timestamp = current_datetime
        otp_obj.save()
        return otp_obj.otp, 'OTP resent successfully.'
    else:
        # Delete previous expired OTP and create a new one
        OTPMapper.delete_expired_otps(mobile_number)
        otp_obj = OTPMapper.create_otp(mobile_number, generate_otp(), 1)
        return otp_obj.otp, 'OTP sent successfully.'

def verify_otp(mobile_number, user_otp):
    otp_obj = OTPMapper.get_active_otp_by_mobile_number(mobile_number)

    if not otp_obj:
        return False, 'OTP not found. Please request OTP first.'

    if otp_obj.attempts >= MAX_OTP_ATTEMPTS:
        return False, 'Maximum attempts reached. Try again after 30 mins.'

    if otp_obj.otp == user_otp:
        otp_obj.delete()
        return True, 'OTP verified successfully.'

    # otp_obj.attempts += 1
    # otp_obj.save()
    return False, 'Incorrect OTP. Please try again.'
