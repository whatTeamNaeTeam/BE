from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.db import IntegrityError
from team.models import Likes, Team
from user.models import CustomUser
from django_seed import Seed


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--number", default=1, type=int, help="추가하려고 하는 좋아요의 수, 최대 100개까지")

    def handle(self, *args, **options):
        number = options.get("number")
        if number > 100:
            raise CommandError("number의 최대 인풋은 100입니다.")
        seeder = Seed.seeder()

        for _ in range(number):
            team = Team.objects.order_by("?").first()
            user = CustomUser.objects.order_by("?").first()

            seeder.add_entity(
                Likes,
                1,
                {
                    "team": team,
                    "user": user,
                },
            )

            try:
                seeder.execute()
                team.like += 1
                team.version += 1
                team.save()

            except IntegrityError:
                print(f"중복된 데이터 발생, 예상 데이터 주입 개수 {number-1}개")
                number -= 1
                continue
        if number:
            self.stdout.write(self.style.SUCCESS(f"{number}개의 더미 좋아요 생성 완료"))
        else:
            self.stdout.write(self.style.ERROR("데이터 주입 실패"))
