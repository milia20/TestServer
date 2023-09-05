from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    groups = None
    objects = UserManager()


class UploadFile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User,  models.CASCADE)
    file = models.FileField()
