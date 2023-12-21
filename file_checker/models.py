from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# Create your models here.


class Task(models.Model):
    title = models.CharField('Название', max_length=30)
    task = models.TextField('Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'tast'
        verbose_name_plural = 'tasts'


class MyUser(AbstractUser):
    groups = None
    objects = UserManager()


class UploadedFile(models.Model):
    owner = models.ForeignKey(MyUser, models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField('Название', max_length=50, default='0000000')
    file = models.FileField()

    def __str__(self):
        return str(self.created)

    class Meta:
        verbose_name = 'CSV_file'
        verbose_name_plural = 'CSV_files'




# #
# class UploadedFile(models.Model):
#     created = models.DateTimeField(auto_now_add=True)
#     owner = models.ForeignKey(MyUser,  models.CASCADE)
#     file = models.FileField()