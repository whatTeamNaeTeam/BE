from PIL import Image
import boto3
import io
import uuid

import wtnt.settings as settings


class S3Utils:
    USER_THUMNAIL = (200, 200)
    TEAM_THUMNAIL = (320, 180)

    client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_CLIENT_ID,
        aws_secret_access_key=settings.AWS_CLIENT_SECRET,
        region_name=settings.AWS_REGION,
    )
    bucket = settings.BUCKET_NAME
    region = settings.AWS_REGION

    @classmethod
    def create_thumnail(cls, image, category):
        img = Image.open(image)
        img = img.convert("RGB")
        img.thumbnail(cls.USER_THUMNAIL if category == "user" else cls.TEAM_THUMNAIL)

        img_io = io.BytesIO()
        img.save(img_io, format="JPEG")
        img_io.seek(0)

        return img_io

    @staticmethod
    def get_team_image_name(id):
        return "team/" + str(id) + "/"

    @staticmethod
    def get_user_image_name(id):
        return "user/" + str(id) + "/"

    @classmethod
    def upload_team_image_on_s3(cls, image, id=None):
        s3_client = cls.client
        if id is None:
            _uuid = uuid.uuid4()
        else:
            _uuid = id

        if image is None:
            return f"https://{cls.bucket}.s3.{cls.region}.amazonaws.com/default/", _uuid

        root = cls.get_team_image_name(_uuid)
        thumnail = cls.create_thumnail(image, "team")
        s3_client.upload_fileobj(thumnail, cls.bucket, root + "thumnail.jpg")

        image.seek(0)
        s3_client.upload_fileobj(image, cls.bucket, root + "image.jpg")

        return f"https://{cls.bucket}.s3.{cls.region}.amazonaws.com/{root}", _uuid

    @classmethod
    def delete_team_image_on_s3(cls, id):
        s3_client = cls.client
        root = cls.get_team_image_name(id)
        s3_client.delete_object(Bucket=cls.bucket, Key=root + "image.jpg")
        s3_client.delete_object(Bucket=cls.bucket, Key=root + "thumnail.jpg")

    @classmethod
    def upload_user_image_on_s3(cls, id, image):
        s3_client = cls.client
        root = cls.get_user_image_name(id)
        thumnail = cls.create_thumnail(image, "user")
        s3_client.upload_fileobj(thumnail, cls.bucket, root + "thumnail.jpg")

        image.seek(0)
        s3_client.upload_fileobj(image, cls.bucket, root + "image.jpg")

        return f"https://{cls.bucket}.s3.{cls.region}.amazonaws.com/{root}"

    @classmethod
    def delete_user_image_on_s3(cls, id):
        s3_client = cls.client
        root = cls.get_user_image_name(id)
        s3_client.delete_object(Bucket=cls.bucket, Key=root + "image.jpg")
        s3_client.delete_object(Bucket=cls.bucket, Key=root + "thumnail.jpg")
