import boto3

from django_redis import get_redis_connection

from team.models import Likes
import wtnt.settings as settings


client = get_redis_connection()


class TeamResponse:
    @staticmethod
    def get_team_list_response(team_data, user_id, is_manage=None):
        if is_manage:
            for d in team_data:
                if d["leader_info"]["id"] == user_id:
                    d["leader_info"]["is_leader"] = True
        else:
            team_ids = []
            for d in team_data:
                team_ids.append(d["id"])

            likes = TeamResponse.is_likes(team_ids, user_id)

            for d, like in zip(team_data, likes):
                d["is_like"] = like

        return team_data

    @staticmethod
    def is_likes(team_ids, user_id):
        likes = Likes.objects.team_ids(user_id=user_id, team_ids=team_ids)

        result = [False] * len(team_ids)

        likes_dict = {like["team_id"]: like["exists"] for like in likes}
        for idx, team_id in enumerate(team_ids):
            result[idx] = likes_dict.get(team_id, False)

        return result

    @staticmethod
    def is_like(team_id, user_id):
        try:
            Likes.objects.get(team_id=team_id, user_id=user_id)
            return True
        except Likes.DoesNotExist:
            return False

    @staticmethod
    def is_leader(leader_id, user_id):
        return user_id == leader_id

    @staticmethod
    def make_data(leader, strs, image, categories, counts):
        _dict = {
            "title": strs.get("name"),
            "leader_id": leader,
            "explain": strs.get("explain"),
            "genre": strs.get("genre"),
            "image": image,
            "url": strs.get("urls", []),
            "category": TeamResponse.make_tech_data(categories, counts),
        }

        return _dict

    @staticmethod
    def make_tech_data(categories, counts):
        return [{"tech": category, "need_num": count} for category, count in zip(categories, counts)]

    @staticmethod
    def get_detail_response(team_data, user_id):
        url_data = team_data.pop("url")
        url_data = url_data.split(",") if url_data else []
        team_data["urls"] = url_data

        leader_id = team_data["leader_info"]["id"]
        team_id = team_data["id"]

        return {
            "team": team_data,
            "is_leader": TeamResponse.is_leader(leader_id, user_id),
            "is_like": TeamResponse.is_like(team_id, user_id),
        }


class ApplyResponse:
    @staticmethod
    def make_data(user_id, team_id, bio, tech):
        return {"team_id": team_id, "user_id": user_id, "bio": bio, "tech": tech, "is_approved": False}


class LikeResponse:
    @staticmethod
    def make_data(like_num, is_like, version):
        return {"like": {"like_count": like_num, "is_like": is_like}, "version": version}


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


class RedisTeamUtils:
    @staticmethod
    def sadd_view_client(team_id, user_id, adress):
        return client.sadd(f"views:{team_id}", f"{user_id}_{adress}")
