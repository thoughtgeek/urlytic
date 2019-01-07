import os
import random
from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

def randomizer(instance, filename):
    basefilename, file_extension= os.path.splitext(filename)
    chars= 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr= ''.join((random.choice(chars)) for x in range(10))
    basefilename = basefilename[:10]
    return '{basename}_{randomstring}{ext}'.format(basename= basefilename, randomstring= randomstr, ext= file_extension)

class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(upload_to=randomizer, null=True)
    uploader = models.ForeignKey(User, db_column="user")
    def __str__(self):
        return self.upload.name

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