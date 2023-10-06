from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    path('', views.get_data),
    path('add/', views.add_item)
]
