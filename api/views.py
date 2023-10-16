import re
import geopy.distance
import os
import googlemaps

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import ParkingSpace, Reservation
from .serializers import ParkingSpaceSerializer, ReservationSerializer
from dotenv import load_dotenv


load_dotenv()

google_api_key = os.getenv('KEY')
gmaps = googlemaps.Client(key=google_api_key)


@api_view(['GET'])
def get_all_parking_space_data(request):
    parking_spaces = ParkingSpace.objects.all()
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

#this is not working
@api_view(['POST'])
def add_reservation_item(request):
    driver_phone_number = _format_phone_number(request.data["driver_phone_number"])
    request.data["driver_phone_number"] = driver_phone_number
    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_reservations(request, phone_number):
    formatted_phone_number = _format_phone_number(phone_number)
    user_reservations = Reservation.objects.filter(driver_phone_number=formatted_phone_number)
    serializer = ReservationSerializer(user_reservations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_parking_reservations(request, phone_number):
    formatted_phone_number = _format_phone_number(phone_number)
    user_reservations = Reservation.objects.filter(parking_id__phone_number=formatted_phone_number)
    serializer = ReservationSerializer(user_reservations, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_reservation(request):
    formatted_phone_number = _format_phone_number(request.data["phone_number"])
    ticket_code = request.data["ticket_code"]
    del request.data["ticket_code"]
    del request.data["phone_number"]
    user_reservations = Reservation.objects.filter(driver_phone_number=formatted_phone_number, ticket_code=ticket_code)

    if not user_reservations:
        return Response({"message": "Reservation not found"}, status=404)

    user_reservation = user_reservations[0]
    new_user_reservation_data = request.data

    serializer = ParkingSpaceSerializer(user_reservation, data=new_user_reservation_data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Parking space updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
def update_parking_space(request):
    formatted_phone_number = _format_phone_number(request.data["phone_number"])
    del request.data["phone_number"]
    parking_spaces = ParkingSpace.objects.filter(phone_number=formatted_phone_number)

    if not parking_spaces:
        return Response({"message": "Parking space not found"}, status=404)

    parking_space = parking_spaces[0]
    new_parking_space_data = request.data

    serializer = ParkingSpaceSerializer(parking_space, data=new_parking_space_data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Parking space updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def search_nearby_parking_spaces(request):
    longitude = request.GET.get('longitude')
    latitude = request.GET.get('latitude')
    request_coords = (latitude, longitude)
    nearby_parking_spaces = []

    results = gmaps.places_nearby(
        location=request_coords,
        radius=500,
        type='parking'  # Isso busca estacionamentos.
    )

    for result in results['results']:
        parking_spaces = ParkingSpace.objects.filter(place_id=result['place_id'])
        if len(parking_spaces) == 0:
            if 'rating' not in result:
                result['rating'] = 0
            if 'user_ratings_total' not in result:
                result['user_ratings_total'] = 0

            place_detail = gmaps.place(result['place_id'], session_token=None, fields=None, language=None, reviews_no_translations=False,
                        reviews_sort='most_relevant')['result']
            phone_number = place_detail.get("formatted_phone_number") or place_detail.get("international_phone_number")
            images = [None]
            formatted_working_hours = _format_working_hours(place_detail.get('current_opening_hours').get('weekday_text')) \
                if 'current_opening_hours' in place_detail else None
        else:
            phone_number = str(parking_spaces[0].phone_number)
            images = parking_spaces[0].images
            formatted_working_hours = parking_spaces[0].working_hours

        if phone_number:
            formatted_phone_number = _format_phone_number(phone_number)
            parking_lat, parking_long = result.get('geometry').get('location').get('lat'), result.get('geometry').get('location').get('lng')
            parking_coords = (parking_lat, parking_long)
            distance = geopy.distance.geodesic(request_coords, parking_coords).km

            parking_space = {
                "latitude": result['geometry']['location']['lat'],
                "longitude": result['geometry']['location']['lng'],
                "name": result['name'],
                "place_id": result['place_id'],
                "address": result['vicinity'],
                "distance": distance,
                "price": None,
                "rate": f"{result.get('rating')} ({result.get('user_ratings_total')})",
                "day_time": None,
                "working_hours": formatted_working_hours,
                "payment_options": None,
                "open_parking_spot": None,
                "total_parking_spot": None,
                "open_schedule_parking_spot": None,
                "total_schedule_parking_spot": None,
                "phone_number": formatted_phone_number,
                "available_schedules": None,
                "price_table": None,
                "images": images
            }

            serializer = ParkingSpaceSerializer(data=parking_space)
            if serializer.is_valid():
                serializer.save()
            nearby_parking_spaces.append(parking_space)

    return Response(nearby_parking_spaces)


def _format_working_hours(list_of_working_hours_with_unicode):
    working_hours = {}
    translated_days = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    for working_hours_with_unicode in list_of_working_hours_with_unicode:
        working_hours_decode = working_hours_with_unicode.encode("ascii", "ignore").decode()
        pattern = r"([aA-zZ]+):\s(\d+:\d+[APap][Mm])(\d+:\d+[APap][Mm])"
        match = re.match(pattern, working_hours_decode)
        if match:
            day, start_time, end_time = match.groups()
            translated_day = translated_days[day]
            working_hours[translated_day] = f"{start_time} às {end_time}"
            del translated_days[day]

    for day in translated_days.values():
        working_hours[day] = "Not filled"

    return working_hours


def _format_phone_number(phone_number):
    numbers = ''.join(re.findall(r'\d+', phone_number))
    return re.sub(r'(\d{2})?(\d{2})(\d{8,9})', r'+55 (\2) \3', numbers)
