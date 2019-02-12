from django.urls import path, include
from feedback import views

urlpatterns = [
    path('', views.feedback),
    path('feedback/', views.feedback),
]