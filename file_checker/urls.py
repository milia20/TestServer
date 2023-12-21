from django.urls import path
from . import views

app_name = 'file_checker'

urlpatterns = [
    path(r"", views.index, name="main"),
    path(r"file_checker", views.upload, name="upload-task"),
    path(r'upload-file/', views.FileUploadAPIView.as_view(), name='upload-file'),

    path(r'upload/', views.Uploader.as_view(), name='upload'),
    path('drop/<str:filename>/', views.Dropper.as_view())

]
