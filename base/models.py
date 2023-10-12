import json
from datetime import datetime

from django.db import models

# Create your models here.
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField


class ParkingSpace(models.Model):
    class PaymentOptions(models.TextChoices):
        CREDIT_CARD = 'CREDIT_CARD', 'Cartão de Crédito'
        DEBIT_CARD = 'DEBIT_CARD', 'Cartão de Débito'
        PIX = 'PIX', 'Pix'
        CASH = 'CASH', 'Dinheiro'

    def clean(self):
        # Validate required days
        required_days = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

        for day in required_days:
            if day not in self.working_hours:
                raise ValidationError(f"Missing data for {day}")

        super().clean()

    created_date = models.DateField(auto_now_add=True,blank=True, null=True)
    place_id = models.TextField(default="PLACE_ID", unique=True, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    rate = models.CharField(max_length=50, blank=True, null=True)
    working_hours = models.JSONField(blank=True, null=True)
    payment_options = ArrayField(models.CharField(max_length=50, choices=PaymentOptions.choices), blank=True, null=True)
    open_parking_spot = models.IntegerField(blank=True, null=True)
    total_parking_spot = models.IntegerField(blank=True, null=True)
    open_schedule_parking_spot = models.IntegerField(blank=True, null=True)
    total_schedule_parking_spot = models.IntegerField(blank=True, null=True)
    phone_number = PhoneNumberField(region='BR', blank=True, null=True)
    available_schedules = models.JSONField(blank=True, null=True)
    price_table = models.JSONField(blank=True, null=True)
    images = ArrayField(models.TextField(), blank=True, null=True)


class Reservation(models.Model):
    class TicketStatus(models.TextChoices):
        APPROVED = 'APPROVED', 'Confirmada'
        WAITING = 'WAITING', 'Aguardando estacionamento'
        CANCELLED = 'CANCELLED', 'Cancelada'

    parking_id = models.ForeignKey(ParkingSpace, on_delete=models.DO_NOTHING)
    ticket_date_and_time = models.DateTimeField()
    ticket_status = models.CharField(max_length=30, choices=TicketStatus.choices, default=TicketStatus.WAITING)
    created_date = models.DateField(auto_now_add=True)
    ticket_code = models.CharField(max_length=30, default=datetime.now().strftime("%d%m%Y%H%M%S"))
    driver_car = models.CharField(max_length=200)
    driver_phone_number = PhoneNumberField(region='BR')
    driver_name = models.CharField(max_length=200)
