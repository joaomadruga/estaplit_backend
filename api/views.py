from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import ParkingSpace, Reservation
from .serializers import ParkingSpaceSerializer, ReservationSerializer


@api_view(['GET'])
def get_all_parking_space_data(request):
    parking_spaces = ParkingSpace.objects.all()
    print(parking_spaces)
    serializer = ParkingSpaceSerializer(parking_spaces, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_parking_space_item(request):
    serializer = ParkingSpaceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(f'JSON Content not valid {serializers.ValidationError(serializer.errors)}')


@api_view(['GET'])
def get_all_reservation_data(request):
    reservation = Reservation.objects.all()
    serializer = ReservationSerializer(reservation, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_reservation_item(request):
    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(f'JSON Content not valid {serializers.ValidationError(serializer.errors)}')
