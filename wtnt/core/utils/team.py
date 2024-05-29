from team.models import Likes


def make_team_list(team_data, user_id, is_manage=None):
    if is_manage:
        for d in team_data:
            if d["leader_id"] == user_id:
                d["is_leader"] = True
    else:
        team_ids = []
        for d in team_data:
            team_ids.append(d["id"])

        likes = is_likes(team_ids, user_id)

        for d, like in zip(team_data, likes):
            d["is_like"] = like

    return team_data


def is_likes(team_ids, user_id):
    likes = Likes.objects.team_ids(user_id=user_id, team_ids=team_ids)

    result = [False] * len(team_ids)

    likes_dict = {like["team_id"]: like["exists"] for like in likes}
    for idx, team_id in enumerate(team_ids):
        result[idx] = likes_dict.get(team_id, False)

    return result
