from __future__ import unicode_literals

from django.db import models
import os


class Car(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True, default=0)
    prev_price = models.FloatField(null=True, blank=True, default=0)
    updated_on = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'CarPrice'

