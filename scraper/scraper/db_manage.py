#!/usr/bin/python
import os
from os import sys, path
import MySQLdb

# print path.dirname(path.dirname(path.abspath(__file__))), '@@@@@'
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_price.settings")

from project.models import *

def getDB():
    return MySQLdb.connect(host="localhost",    # your host, usually localhost
                           user="root",         # your username
                           passwd="newfirst",   # your password
                           db="Car")            # name of the data base


def getGenre(db):
    res = dict()

    cur = db.cursor()
    cur.execute("SELECT * FROM Genre")

    # print all the first cell of all the rows
    for row in cur.fetchall():
        if row[1] not in res:
            res[row[1]] = dict()
        res[row[1]][row[2]] = row[3]


    # print Make.objects.count(), '@@@@@@'
    return res

def save(db, item):
    cur = db.cursor()

    # check if a car is in db.
    sql = "SELECT * FROM CarPrice WHERE car_id={}".format(item["car_id"]) 
    cur.execute(sql)

    if len(cur.fetchall()) == 0:
        sql = "insert into CarPrice (car_id, name, country, brand, year, price, prev_price, updated_on, updated) values(%s, '%s', '%s', '%s', %d, %d, %d, Now(), 1)" % (item['car_id'], item["name"], item["country"], item["model"], item["year"], item["price"], item["price"])
    else:
        sql = "update CarPrice set prev_price=price, price=%d, updated=1 where car_id=%s" % (item["price"], item["car_id"])

    cur.execute(sql)
    db.commit()

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
    