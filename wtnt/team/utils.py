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


createSerializerHelper = TeamCreateSerializerHelper()
