import boto3

import wtnt.settings as settings


class S3Utils:
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_CLIENT_ID,
        aws_secret_access_key=settings.AWS_CLIENT_SECRET,
        region_name=settings.AWS_REGION,
    )
    bucket = settings.BUCKET_NAME
    region = settings.AWS_REGION

    @staticmethod
    def get_team_image_name(name):
        return "team/" + name + "/image.jpg"

    @classmethod
    def upload_team_image_on_s3(cls, name, image):
        s3_client = cls.client
        root = cls.get_team_image_name(name)
        s3_client.upload_fileobj(image, cls.bucket, root)

        return f"https://{cls.bucket}.s3.{cls.region}.amazonaws.com/{root}"

    @classmethod
    def delete_team_image_on_s3(cls, name):
        s3_client = cls.client
        root = cls.get_team_image_name(name)
        s3_client.delete_object(Bucket=cls.bucket, Key=root)
