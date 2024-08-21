from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.conf import settings
from team.models import Team, TeamUser, TeamTech
from user.models import CustomUser
from django_seed import Seed
from faker import Faker

from itertools import cycle
import random
import uuid


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--number", default=1, type=int, help="추가하려고 하는 팀의 수, 최대 100개까지")

    def handle(self, *args, **options):
        faker = Faker("ko_KR")
        number = options.get("number")
        if number > 100:
            raise CommandError("number의 최대 인풋은 100입니다.")
        seeder = Seed.seeder()
        genres = ["웹", "앱", "게임"]
        categories = [
            "웹",
            "IOS",
            "안드로이드",
            "크로스플랫폼",
            "자바",
            "파이썬",
            "노드",
            "UI/UX 기획",
            "게임 기획",
            "컨텐츠 기획",
            "프로젝트 매니저",
            "유니티",
            "언리얼",
            "딥러닝",
            "머신러닝",
            "데이터 엔지니어",
            "게임 그래픽 디자인",
            "UI/UX 디자인",
        ]
        leaders = [CustomUser.objects.order_by("?").first() for _ in range(number)]
        leader_cycle = cycle(leaders)

        seeder.add_entity(
            Team,
            number,
            {
                "leader": lambda x: next(leader_cycle),
                "title": lambda x: faker.catch_phrase(),
                "explain": lambda x: faker.catch_phrase().encode(),
                "uuid": lambda x: uuid.uuid4(),
                "genre": lambda x: random.choice(genres),
                "like": 0,
                "view": 0,
                "version": 0,
                "url": lambda x: faker.url().encode(),
                "is_approved": True,
                "is_accomplished": False,
                "image": f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/default",
            },
        )

        team_ids = seeder.execute()[Team]

        for team_id, user in zip(team_ids, leader_cycle):
            team = Team.objects.get(pk=team_id)
            seeder.add_entity(
                TeamUser,
                1,
                {
                    "user": user,
                    "team": team,
                    "tech": "팀장",
                },
            )

            seeder.execute()

            seeder.add_entity(
                TeamTech,
                1,
                {
                    "current_num": 0,
                    "need_num": random.randint(1, 10),
                    "team": team,
                    "tech": random.choice(categories),
                },
            )

        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number}개의 더미 팀 생성 완료. 팀 ID: {team_ids}"))
