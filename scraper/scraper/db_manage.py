#!/usr/bin/python
import os
from os import sys, path
import MySQLdb
import django


sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_price.settings")
django.setup()

from project.models import *

def getDB():
    return MySQLdb.connect(host="localhost",    # your host, usually localhost
                           user="root",         # your username
                           passwd="newfirst",   # your password
                           db="Car")            # name of the data base


def getGenre(db):
    genre = {}
    for make in Make.objects.all():
        genre[make.name] = {'alias': make.alias}
        for model in Model.objects.filter(make=make):
            year_filter = [{'from': item.from_year, 'to': item.to_year} for item in YearFilter.objects.filter(model=model)]
            genre[make.name][model.name] = {'alias': model.alias}
            genre[make.name][model.name]['year_filter'] = year_filter

    return genre


def save(db, item):
    car = Car.objects.filter(car_id=item["car_id"]).first()
    if car:
        car.prev_price = car.price
        car.price = item["price"]
    else:
        car = Car(**item)
    car.save()



def setUpdateFlag(db):
    cur = db.cursor()
    # cur.execute("update CarPrice set updated=0")
    cur.execute("update CarPrice set updated=0 where country='USA'")
    db.commit()


def removeNotCar(db):
    cur = db.cursor()
    # cur.execute("delete from CarPrice where updated=0")
    cur.execute("delete from CarPrice where updated=0 and country='USA'")
    db.commit()
    