#!/usr/bin/python
import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_price.settings")
django.setup()

from project.models import *


def getGenre():
    genre = {}
    for make in Make.objects.all():
        make_name = make.name.lower().strip()
        genre[make_name] = {'alias': make.alias}
        for model in Model.objects.filter(make=make):
            year_filter = [{'from': item.from_year, 'to': item.to_year} for item in YearFilter.objects.filter(model=model)]
            model_name = model.name.lower().strip()

            genre[make_name][model_name] = {'alias': model.alias}
            genre[make_name][model_name]['year_filter'] = year_filter
            genre[make_name][model_name]['min_price'] = model.min_price
            genre[make_name][model_name]['max_price'] = model.max_price

    return genre
    

def save(item):
    car = Car.objects.filter(car_id=item["car_id"]).first()
    if car:
        car.prev_price = car.price
        car.price = item["price"]
        car.updated = 1
    else:
        car = Car(**item)
    car.save()


def setUpdateFlag():
    # Car.objects.all().update(updated=0)       ##@@##
    pass


def removeNotCar():
    # Car.objects.filter(updated=0).delete()    ##@@##
    pass
    