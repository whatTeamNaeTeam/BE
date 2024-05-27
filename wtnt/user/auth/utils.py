from django.core.cache import cache
from django_redis import get_redis_connection
from datetime import datetime, timedelta

client = get_redis_connection()


def set_refresh_token_in_cache(user_id, refresh_token):
    cache.set(user_id, refresh_token)
    cache.expire_at(user_id, datetime.now() + timedelta(days=7))


def get_refresh_token_in_cache(user_id):
    return cache.get(user_id)


def set_code_in_redis_from_email(email, code):
    client.set(email, code)


def get_code_in_redis_from_email(email):
    return client.get(email).decode()


def delete_code_in_redis_from_email(email):
    client.delete(email)


def get_user_info(user):
    return {
        "name": user.name,
        "student_num": user.student_num,
        "id": user.id,
        "image": user.image,
    }
