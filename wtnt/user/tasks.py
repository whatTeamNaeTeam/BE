import string
import secrets

from django_redis import get_redis_connection
from django.core.mail import EmailMessage

from wtnt.celery import app

client = get_redis_connection("default")


def make_random_code_for_register():
    digit_and_alpha = string.ascii_letters + string.digits
    return "".join(secrets.choice(digit_and_alpha) for _ in range(6))


def get_template(code):
    return """
            <table cellpadding="0" cellspacing="0" border="0" style="width:500px;padding-top:60px">
                <tbody>
                    <tr>
                    <td><img src="https://github.com/03hoho03/whatMeow/assets/71972587/6d2fefea-9b40-40eb-abb2-dcb7e18ae396" width="99" height="54" border="0" alt="WhatMeow" class="CToWUd" data-bit="iit"></a></td>
                    </tr>
                    <tr>
                    <td
                        style="padding-top:25px;font:bold 32px 'Malgun Gothic',dotum,verdana,serif;color:#17191d;letter-spacing:-1.5px">
                        WTNT 회원가입 코드 안내</td>
                    </tr>
                    <tr>
                    <td
                        style="padding:20px 0 30px;font:14px 'Malgun Gothic',dotum,verdana,serif;color:#4a4e57;letter-spacing:-0.7px;line-height:1.71">
                        안녕하세요, <strong style="color:#17191d;word-break:break-all;word-wrap:break-word">신규 회원가입</strong> 고객님<br>
                        고객님의 인증 코드는 <strong style="color:#17191d;word-break:break-all;word-wrap:break-word">{}</strong> 입니다.
                    </td>
                    </tr>
                </tbody>
            </table>
        """.format(
        code
    )


@app.task
def send_email(email):
    code = make_random_code_for_register()
    client.set(email, code, ex=300)
    message = get_template(code)
    subject = "%s" % "[WTNT] 이메일 인증 코드 안내"
    to = [email]
    mail = EmailMessage(subject=subject, body=message, to=to)
    mail.content_subtype = "html"
    mail.send()
    return "Success to send email"
