from datetime import timedelta
from django_redis import get_redis_connection


class RedisUtils:
    client = None

    @classmethod
    def init(cls):
        if not cls.client:
            cls.client = get_redis_connection()

    @classmethod
    def sadd_view_client(cls, team_id, user_id, adress):
        RedisUtils.init()
        return cls.client.sadd(f"views:{team_id}", f"{user_id}_{adress}")

    @classmethod
    def set_refresh_token(cls, user_id, refresh_token):
        RedisUtils.init()
        ttl_seconds = timedelta(days=7).total_seconds()
        cls.client.setex(user_id, int(ttl_seconds), refresh_token)

    @classmethod
    def get_refresh_token(cls, user_id):
        RedisUtils.init()
        return cls.client.get(user_id).decode()

    @classmethod
    def set_code_in_redis_from_email(cls, email, code):
        RedisUtils.init()
        cls.client.set(email, code)

    @classmethod
    def get_code_in_redis_from_email(cls, email):
        RedisUtils.init()
        return cls.client.get(email).decode()

    @classmethod
    def delete_code_in_redis_from_email(cls, email):
        RedisUtils.init()
        cls.client.delete(email)
