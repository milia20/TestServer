from django.contrib import admin

# Register your models here.
from .models import Task, UploadedFile, MyUser


admin.site.register(Task)
admin.site.register(UploadedFile)
admin.site.register(MyUser)
