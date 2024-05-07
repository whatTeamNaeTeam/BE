import wtnt.settings as settings
import boto3


class TeamCreateSerializerHelper:
    def upload_s3(self, name, image):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_CLIENT_ID,
            aws_secret_access_key=settings.AWS_CLIENT_SECRET,
            region_name=settings.AWS_REGION,
        )
        root = "team/" + name + "/image.jpg"
        s3_client.upload_fileobj(image, settings.BUCKET_NAME, root)

        return f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{root}"

    def make_data(self, leader, strs, image, categories, counts):
        _dict = {
            "name": strs.get("name"),
            "leader_id": leader,
            "explain": strs.get("explain"),
            "genre": strs.get("genre"),
            "image": image,
            "url": strs.get("urls", "No"),
            "category": self.make_tech_data(categories, counts),
        }

        return _dict

    def make_tech_data(self, categories, counts):
        return [{"tech": category, "need_num": count} for category, count in zip(categories, counts)]

    def make_response(self, team_data, is_leader):
        url_data = team_data.pop("url")
        if url_data == "No":
            url_data = []
        else:
            url_data = url_data.split(",")

        team_data["urls"] = url_data

        return {"team": team_data, "is_leader": is_leader}


class ApplySerializerHelper:
    def make_data(self, user_id, team_id, bio, tech):
        return {"team_id": team_id, "user_id": user_id, "bio": bio, "tech": tech, "is_approved": False}


applySerializerHelper = ApplySerializerHelper()
createSerializerHelper = TeamCreateSerializerHelper()
