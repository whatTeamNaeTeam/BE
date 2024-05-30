import boto3

from team.models import Likes
import wtnt.settings as settings


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


def make_data(leader, strs, image, categories, counts):
    _dict = {
        "name": strs.get("name"),
        "leader_id": leader,
        "explain": strs.get("explain"),
        "genre": strs.get("genre"),
        "image": image,
        "url": strs.get("urls", "No"),
        "category": make_tech_data(categories, counts),
    }

    return _dict


def make_tech_data(categories, counts):
    return [{"tech": category, "need_num": count} for category, count in zip(categories, counts)]


class S3Utils:
    @staticmethod
    def upload_s3(name, image):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_CLIENT_ID,
            aws_secret_access_key=settings.AWS_CLIENT_SECRET,
            region_name=settings.AWS_REGION,
        )
        root = "team/" + name + "/image.jpg"
        s3_client.upload_fileobj(image, settings.BUCKET_NAME, root)

        return f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{root}"
