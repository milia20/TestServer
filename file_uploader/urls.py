from django.urls import path, re_path

#import TestTask.file_uploader.views
from file_uploader import views

urlpatterns = [
    path('upload/', views.Uploader.as_view(), name='upload'),
    path('', views.index, name='index'),
    #path('info/<slug:filter>/', views.filter, name='filter')
    path('drop/<str:filename>/', views.Dropper.as_view())
    #re_path(r'^info/(\?filter=\w+)*', views.filter, name='filter')
]