from django_redis import get_redis_connection
from django.core.mail import EmailMessage

from wtnt.celery import app
from .utils import sendEmailHelper

client = get_redis_connection("default")


@app.task
def send_email(email):
    code = sendEmailHelper.make_random_code_for_register()
    client.set(email, code, ex=300)
    message = sendEmailHelper.get_template(code)
    subject = "%s" % "[WTNT] 이메일 인증 코드 안내"
    to = [email]
    mail = EmailMessage(subject=subject, body=message, to=to)
    mail.content_subtype = "html"
    mail.send()
    return "Success to send email"
