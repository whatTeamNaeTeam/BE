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
