from django.urls import path, include
from feedback import views

urlpatterns = [
    path('feedback/', views.feedback),
]