from django.db import models
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from apps.home.models import Document


class UrlMap(models.Model):
    document = models.ForeignKey(Document, default=None, on_delete=models.CASCADE)
    full_url = models.CharField(max_length=256)
    short_url = models.CharField(max_length=50, unique=True, db_index=True)
    usage_count = models.IntegerField(default=0)
    max_count = models.IntegerField(default=-1)
    lifespan = models.IntegerField(default=-1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField()
    enabled = models.CharField(max_length=5)
    webhook = models.URLField(max_length=255, default=None, null=True, blank=True)

    def __str__(self):
        return self.full_url

