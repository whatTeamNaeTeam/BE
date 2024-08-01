from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from user.models import CustomUser
from django_seed import Seed
from faker import Faker
import random


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--number", default=1, type=int, help="추가하려고 하는 유저의 수")

    def handle(self, *args, **options):
        faker = Faker("ko_KR")
        number = options.get("number")
        seeder = Seed.seeder()
        positions = ["백엔드", "프론트엔드", "AI", "디자이너"]

        seeder.add_entity(
            CustomUser,
            number,
            {
                "email": lambda x: faker.unique.email(),
                "social_id": lambda x: faker.unique.random_number(digits=9, fix_len=True),
                "name": lambda x: faker.name(),
                "student_num": lambda x: faker.unique.random_number(digits=9, fix_len=True),
                "position": lambda x: random.choice(positions),
                "explain": "열심히 하겠습니다!",
                "university": "부경대학교",
                "club": "WAP",
                "password": "password",
                "is_superuser": False,
                "is_approved": True,
                "is_active": True,
                "is_staff": False,
                "image": f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/default/",
            },
        )

        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number}명의 더미 유저 생성 완료."))
