from rest_framework import serializers
from base.models import ParkingSpace, Reservation


class ParkingSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpace
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    parking_address = serializers.CharField(source='parking_id.address')
    parking_name = serializers.CharField(source='parking_id.name')

    class Meta:
        model = Reservation
        fields = ["ticket_date_and_time", "ticket_status", "driver_car", "driver_phone_number", "driver_name", "parking_address",
                  "ticket_code", "parking_name"]

