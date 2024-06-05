from datetime import datetime, timedelta

from django.core.cache import cache
from django_redis import get_redis_connection

client = get_redis_connection()


class RedisUtils:
    @staticmethod
    def sadd_view_client(team_id, user_id, adress):
        return client.sadd(f"views:{team_id}", f"{user_id}_{adress}")

    @staticmethod
    def set_refresh_token_in_cache(user_id, refresh_token):
        cache.set(user_id, refresh_token)
        cache.expire_at(user_id, datetime.now() + timedelta(days=7))

    @staticmethod
    def get_refresh_token_in_cache(user_id):
        return cache.get(user_id)

    @staticmethod
    def set_code_in_redis_from_email(email, code):
        client.set(email, code)

    @staticmethod
    def get_code_in_redis_from_email(email):
        return client.get(email).decode()

    @staticmethod
    def delete_code_in_redis_from_email(email):
        client.delete(email)
