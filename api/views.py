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
        print(result)
        parking_space = {
            "latitude": result["geometry"]['location']['lat'],
            "longitude": result["geometry"]['location']['lng'],
            "name": result['name'],
            "place_id": result['place_id'],
            "address": result['vicinity'],
            "distance": "",
            "price": "",
            "rate": "",
            "day_time": "",
            "working_time": {
                "Segunda-feira": "",
                "Terça-feira": "",
                "Quarta-feira": "",
                "Quinta-feira": "",
                "Sexta-feira": "",
                "Sábado": "",
                "Domingo": ""
            },
            "payment_options": ['CREDIT_CARD', 'DEBIT_CARD', 'PIX', 'CASH'],
            "open_parking_spot": "",
            "total_parking_spot": "",
            "open_schedule_parking_spot": "",
            "total_schedule_parking_spot": "",
            "phone_number": "",
            "available_schedules": [
                {
                    "date":"12/10",
                    "day": "segunda",
                    "hours":[{
                    "hour":"10:00",
                    "available": 4
                    },
                    {
                        "hour":"10:00",
                        "available": 4
                    },
                    {
                        "hour":"10:00",
                        "available": 4
                    },
                    {
                        "hour":"10:00",
                        "available": 4
                    }]
                }
            ],
            "price_table": {
                "Até 20 minutos": "Grátis",
                "4 horas": 11,
                "Hora adicional": 4,
                "Taxa de reserva": 5
            },
            "images": ["https://www.diariodepernambuco.com.br/static/app/noticia_127983242361/2018/07/06/756766/20180706203355962241i.jpg"]
        }

        print(parking_space)

    return Response(results)
    # nearby_parking_spaces = ParkingSpace.objects.filter(latitude__range=(latitude-0.1, latitude+0.1), longitude__range=(longitude-0.1, longitude+0.1))
    # serializer = ParkingSpaceSerializer(nearby_parking_spaces, many=True)
    # return Response(serializer.data)
    # return Response("ok")