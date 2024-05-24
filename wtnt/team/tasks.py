from django_redis import get_redis_connection

from wtnt.celery import app

client = get_redis_connection()


@app.task
def delete_view_history():
    cursor = "0"
    print("--- 팀 조회 히스토리 삭제 시작 ---")
    while cursor != 0:
        cursor, keys = client.scan(cursor=cursor, match="views:*")
        if keys:
            client.delete(*keys)
    print("--- 팀 조회 히스토리 삭제 완료 ---")
    return "Success to delete team-view-history"
