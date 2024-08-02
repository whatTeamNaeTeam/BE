from django.db import models
from django.db.models import Q, Case, When, Value, BooleanField


class LikesQuerySet(models.QuerySet):
    def team_ids(self, user_id, team_ids):
        return (
            self.filter(Q(user_id=user_id) & Q(team_id__in=team_ids))
            .values("team_id")
            .annotate(
                exists=Case(When(user_id=user_id, then=Value(True)), default=Value(False), output_field=BooleanField())
            )
        )


class LikesManager(models.Manager):
    def get_queryset(self):
        return LikesQuerySet(self.model, using=self._db)

    def team_ids(self, user_id, team_ids):
        return self.get_queryset().team_ids(user_id, team_ids)


class TeamQuerySet(models.QuerySet):
    def search_by_name(self, title):
        return self.filter(Q(title__icontains=title), is_approved=True).order_by("id")

    def search_by_genre(self, genre):
        return self.filter(Q(genre__icontains=genre), is_approved=True).order_by("id")

    def search_by_leader_ids(self, leader_ids):
        return self.filter(Q(leader_id__in=leader_ids), is_approved=True).order_by("id")


class TeamManager(models.Manager):
    def get_queryset(self):
        return TeamQuerySet(self.model, using=self._db)

    def search_by_name(self, title):
        return self.get_queryset().search_by_name(title=title)

    def search_by_genre(self, genre):
        return self.get_queryset().search_by_genre(genre=genre)

    def search_by_leader_ids(self, leader_ids):
        return self.get_queryset().search_by_leader_ids(leader_ids=leader_ids)
