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

    def save(self, **kwargs):
        self.clean()
        return super(ParkingSpace, self).save(**kwargs)

    def clean(self):
        # Validate required days
        required_days = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

        for day in required_days:
            if self.working_hours and day not in self.working_hours:
                raise ValidationError(f"Missing data for {day}")

        if self.open_parking_spot and self.total_parking_spot and self.open_parking_spot > self.total_parking_spot:
            raise ValidationError(f"Open parking spot should not be greater than total parking spot.")

        if self.open_schedule_parking_spot and self.total_schedule_parking_spot and self.open_schedule_parking_spot > self.total_schedule_parking_spot:
            raise ValidationError(f"Open schedule parking spot should not be greater than total schedule parking spot.")

        super().clean()

    created_date = models.DateField(auto_now_add=True)
    place_id = models.TextField(unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=200)
    address = models.TextField()
    rate = models.CharField(max_length=50)
    working_hours = models.JSONField(null=True)
    payment_options = ArrayField(models.CharField(max_length=50, choices=PaymentOptions.choices), null=True)
    open_parking_spot = models.IntegerField(null=True)
    total_parking_spot = models.IntegerField(null=True)
    open_schedule_parking_spot = models.IntegerField(null=True)
    total_schedule_parking_spot = models.IntegerField(null=True)
    phone_number = PhoneNumberField(region='BR')
    available_schedules = models.JSONField(null=True)
    price_table = models.JSONField(null=True)
    images = ArrayField(models.TextField(null=True))


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
