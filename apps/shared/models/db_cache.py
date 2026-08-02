from django.db import models


class CacheTable(models.Model):
    cache_key = models.CharField(primary_key=True, max_length=255)
    value = models.TextField()
    expires = models.DateTimeField()

    @classmethod
    def _check_fields(cls, **kwargs):
        return []

    class Meta:
        app_label = "shared"
        db_table = "cache_table"
