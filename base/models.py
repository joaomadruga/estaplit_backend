from django.db import models

# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length=200)
    created_date = models.DateField(auto_now_add=True)
