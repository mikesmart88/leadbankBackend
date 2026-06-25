import requests
from django.conf import settings

def send_mail(recipient_email, mail_info, mail_subj, std_name):
    # Brevo API endpoint for sending transactional emails..
    url = 'https://api.brevo.com/v3/smtp/email'

    # The email data we are sending to the user..
    payload = {
        "sender": {
            "name": f"Leadbank Community",
            "email": "hello@leadbankuniversal.com"
        },
        "to": [
            {
                "email": recipient_email,
                "name": f"{std_name}"
            }
        ],
        "subject": f"{mail_subj}",
        "htmlContent": f"{mail_info}"
    }

    # Our authorization header..
    headers = {
        'api-key': settings.API_KEY,
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }

    # Our post request..
    response = requests.post(url, json=payload, headers=headers)
    return
