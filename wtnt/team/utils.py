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

    def make_data(self, leader, strs, url):
        _dict = {
            "name": strs.get("name"),
            "leader_id": leader,
            "explain": strs.get("explain"),
            "genre": strs.get("genre"),
            "image": url,
        }

        return _dict

    def make_urls_data(self, team_id, urls):
        return [{"team_id": team_id, "url": url} for url in urls]

    def make_techs_data(self, team_id, categories, counts):
        return [
            {"team_id": team_id, "tech": category, "need_num": count} for category, count in zip(categories, counts)
        ]

    def make_full_response(self, team_data, url_data, tech_data):
        return {"team": team_data, "urls": url_data, "category": tech_data}

    def make_response(self, team_data, tech_data):
        return {"team": team_data, "category": tech_data, "urls": None}


class ApplySerializerHelper:
    def make_data(self, user_id, team_id, bio, tech):
        return {"team_id": team_id, "user_id": user_id, "bio": bio, "tech": tech, "is_approved": False}


applySerializerHelper = ApplySerializerHelper()
createSerializerHelper = TeamCreateSerializerHelper()