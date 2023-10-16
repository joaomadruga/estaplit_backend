from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    path('parking_spaces/', views.get_all_parking_space_data),
    path('parking_spaces/add_parking_space/', views.add_parking_space_item),
    path('parking_spaces/get_nearby_parking_spaces/', views.search_nearby_parking_spaces),
    path('parking_spaces/<str:phone_number>', views.get_parking_reservations),
    path('parking_spaces/update_parking_space/', views.update_parking_space),
    path('reservations/', views.get_all_reservation_data),
    path('reservations/add_reservation/', views.add_reservation_item),
    path('reservations/user/<str:phone_number>', views.get_user_reservations),
    path('reservations/update_reservation', views.update_reservation),
]
