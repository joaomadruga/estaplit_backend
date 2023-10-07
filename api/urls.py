from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    path('parking_spaces/', views.get_all_parking_space_data),
    path('add_parking_space/', views.add_parking_space_item),
    path('add_reservation/', views.add_reservation_item),
    path('reservations/', views.get_all_reservation_data)
]
