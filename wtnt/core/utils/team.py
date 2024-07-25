from team.models import Likes


class TeamResponse:
    @staticmethod
    def get_team_list_response(team_data, user_id, is_manage=None, count=None):
        if is_manage:
            for d, c in zip(team_data, count):
                if d["leader_info"]["id"] == user_id:
                    d["leader_info"]["is_leader"] = True
                d["member_count"] = c
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
    def make_data(leader, strs, image, categories, counts, uuid):
        _dict = {
            "title": strs.get("title"),
            "leader_id": leader,
            "explain": strs.get("explain"),
            "genre": strs.get("genre"),
            "image": image,
            "category": TeamResponse.make_tech_data(categories, counts),
            "uuid": uuid,
        }

        if "urls" in strs:
            _dict["url"] = strs["urls"]

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
