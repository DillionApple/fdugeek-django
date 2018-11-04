from django.urls import path, include
from account import views

urlpatterns = [
    path('login/', views.user_login),
    path('register/', views.register),
    path('confirm_register/', views.confirm_register),
    path('logout/', views.user_logout),
    path('detail/', views.user_detail),
    path('change_detail/', views.change_detail),
    path('change_password/', views.change_password),
    path('change_icon/', views.change_icon),
]
