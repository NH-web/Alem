# accounts/twilio_service.py
from twilio.rest import Client
from django.conf import settings

def send_sms(phone, code):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    client.messages.create(
        body=f"Your Alem verification code is {code}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )