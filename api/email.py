import datetime
from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User, PasswordResets

# new_otp = random.randint(100000, 999999)


def send_password_reset_token_via_email(email, subject):
    otp = random.randint(100000, 999999)
    message = f'Your OTP is {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    if PasswordResets.objects.filter(user_email=user_obj).exists():
        update_token = PasswordResets.objects.filter(user_email=user_obj)
        update_token.update(otp_token=otp, created_at=datetime.date.today())
        # otp = 0
    else:
        new_reset_token = PasswordResets.objects.create(
            user_email=user_obj, otp_token=otp, created_at=datetime.date.today())
        new_reset_token.save()


def send_verify_user_token_via_email(email):
    otp = random.randint(100000, 999999)
    message = f'Your OTP is {otp}'
    subject = 'Your Verification Token'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.email_verification_token = otp
    user_obj.save()

def send_contact_us_success_email(email):
    message = "Thanks for contacting us we'll Reach you soon!"
    subject = 'Thanks for contacting us'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])