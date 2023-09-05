from django.contrib import admin

from file_uploader.models import UploadFile, User

admin.site.register(UploadFile)
admin.site.register(User)
