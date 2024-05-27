from django.core.cache import cache
from datetime import datetime, timedelta


def set_refresh_token_in_cache(user_id, refresh_token):
    cache.set(user_id, refresh_token)
    cache.expire_at(user_id, datetime.now() + timedelta(days=7))


def get_refresh_token_in_cache(user_id):
    return cache.get(user_id)


def get_user_info(user):
    return {
        "name": user.name,
        "student_num": user.student_num,
        "id": user.id,
        "image": user.image,
    }
