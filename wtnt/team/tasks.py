from django_redis import get_redis_connection
from .models import Team
from wtnt.celery import app

import pickle

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


@app.task
def update_view_count():
    print("--- 팀 조회수 업데이트 시작 ---")
    team_ids = client.smembers("view_updated")
    client.delete("view_updated")
    team_ids = {int(team_id.decode("utf-8")) for team_id in team_ids}
    teams = Team.objects.filter(id__in=list(team_ids))
    print(f"업데이트 게시물 수 : {len(teams)}")
    for team in teams:
        cached_team = pickle.loads(client.get(f":1:team_detail_{team.id}"))
        team.view = cached_team["view"]

    Team.objects.bulk_update(teams, ["view"])
    print("--- 팀 조회수 업데이트 완료 ---")
