import random
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from account.models import EmailOTP
from threading import Thread



def generate_otp(email):
    code = str(random.randint(100000, 999999))
    EmailOTP.objects.create(email=email, code=code)

    mail_context = {
        'otp_code': code,
        'expiry_minutes': 60,
    }

    send_email(
        [email],
        #cc
        ['shiam.sharif.07@gmail.com'],
        #bcc
        [],
        'Your OTP Code',
        'mail/otp_mail.html',
        mail_context
    )
    
    return code


def send_email(mail_to,cc_list,bcc_list,subject,template,context):

    #set use korle load hoi nah.(na use korel 2-3s load hoi)
    # set is oop concept.
    mail_to_set=set(mail_to)
    cc_list_set=set(cc_list)

    common_emails = mail_to_set.intersection(cc_list_set)

    cc_list_set = cc_list_set - common_emails

    html_body = render_to_string(template, context)

    if len(mail_to) > 0:

        email=  EmailMultiAlternatives(
            subject=subject,
            body=html_body,
            from_email=settings.EMAIL_HOST_USER,
            to=list(mail_to_set),
            cc=list(cc_list_set),
            bcc=list(bcc_list)
        )

        email.attach_alternative(html_body, "text/html")

        try:
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Error sending email: {e}")