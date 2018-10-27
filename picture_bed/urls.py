from django.urls import path

from picture_bed import views

urlpatterns = [
    path("upload/", views.upload_picture)
]
