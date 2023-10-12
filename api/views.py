from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import ParkingSpace, Reservation
from .serializers import ParkingSpaceSerializer, ReservationSerializer
import googlemaps
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key = os.getenv('KEY')
gmaps = googlemaps.Client(key=google_api_key)

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


@api_view(['GET'])
def get_user_reservations(request, phone_number):
    print(phone_number)
    user_reservations = Reservation.objects.filter(driver_phone_number=phone_number)
    serializer = ReservationSerializer(user_reservations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_nearby_parking_spaces(request):
    longitude = request.GET.get('longitude')
    latitude = request.GET.get('latitude')
    loc = (latitude, longitude)
    
    results = gmaps.places_nearby(
        location=loc,
        radius=10000,
        type='parking'  # Isso busca estacionamentos.
    )

    for result in results['results']: 
        if 'rating' not in result:
            result['rating'] = 0
        if 'user_ratings_total' not in result:
            result['user_ratings_total'] = 0

        parking_space = {  
            "latitude": result['geometry']['location']['lat'],
            "longitude": result['geometry']['location']['lng'],
            "name": result['name'],
            "place_id": result['place_id'],
            "address": result['vicinity'],
            "distance": 500,
            "price": "NULL",
            "rate": f"{result['rating']} ({result['user_ratings_total']})",
            "day_time": "NULL",
            "working_hours": {
                "Segunda-feira": "NULL",
                "Terça-feira": "NULL",
                "Quarta-feira": "NULL",
                "Quinta-feira": "NULL",
                "Sexta-feira": "NULL",
                "Sábado": "NULL",
                "Domingo": "NULL"
            },
            "payment_options": ["CASH"],
            "open_parking_spot": 0,
            "total_parking_spot": 0,
            "open_schedule_parking_spot": 0,
            "total_schedule_parking_spot": 0,
            "phone_number": "+55 81900000000",
            "available_schedules": [
                {
                "date":"NULL",
                "day": "NULL",
                "hours":[{
                "hour":"NULL",
                "available": 0
                },
                {
                    "hour":"NULL",
                    "available": 0
                },
                {
                    "hour":"NULL",
                    "available": 0
                },
                {
                    "hour":"10:00",
                    "available": 4
                }]
            }],
                "price_table": {
                    "Até 20 minutos": "NULL",
                    "4 horas": 0,
                    "Hora adicional": 0,
                    "Taxa de reserva": 0
                },
            "images": ["NULL"]
        }

        serializer = ParkingSpaceSerializer(data=parking_space)
        print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
        break
    return Response(results)