from .models import OTP
from .utils import get_current_datetime
from .constants import OTP_EXPIRY_MINUTES
from datetime import timedelta


class OTPMapper:
    @staticmethod
    def get_active_otp_by_mobile_number(mobile_number):
        return OTP.objects.filter(
            mobile_number=mobile_number,
            timestamp__gte=get_current_datetime() - timedelta(minutes=OTP_EXPIRY_MINUTES)
        ).first()

    @staticmethod
    def create_otp(mobile_number, otp, attempts):
        return OTP.objects.create(
            mobile_number=mobile_number,
            otp=otp,
            attempts=attempts
        )

    @staticmethod
    def update_otp(otp_obj, otp, attempts):
        otp_obj.otp = otp
        otp_obj.attempts = attempts
        otp_obj.save()

    @staticmethod
    def delete_expired_otps(mobile_number):
        timestamp_limit = get_current_datetime() - timedelta(minutes=OTP_EXPIRY_MINUTES)
        return OTP.objects.filter(
            mobile_number=mobile_number,
            timestamp__lt=timestamp_limit
        ).delete()
