#!/usr/bin/python
import MySQLdb

def getDB():
    db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="carcompare",  # your password
                     db="Car")        # name of the data base

    return db


def getGenre(db):
    res = dict()

    cur = db.cursor()
    cur.execute("SELECT * FROM Genre")

    # print all the first cell of all the rows
    for row in cur.fetchall():
        if row[1] not in res:
            res[row[1]] = dict()
        res[row[1]][row[2]] = row[3]

    return res

def save(db, item):
    if item["price"] < 1000:
        return

    cur = db.cursor()

    # check if a car is in db.
    sql = "SELECT * FROM CarPrice WHERE country='%s' and name='%s' and brand='%s' and year='%d' and price=%f" % (item["country"], item["name"], item["model"], item["year"], item["price"]) 
    cur.execute(sql)

    if True:#len(cur.fetchall()) == 0:
        sql = "insert into CarPrice (name, country, brand, year, price, prev_price, updated_on, updated) values('%s', '%s', '%s', %d, %f, %f, Now(), 1)" % (item["name"], item["country"], item["model"], item["year"], item["price"], item["price"])
    else:
        sql = "update CarPrice set prev_price=price, price=%s, updated=1 where country='%s' and name='%s' and brand='%s' and year='%d' and price=%f" % (item["price"], item["country"], item["name"], item["model"], item["year"], item["price"])

    cur.execute(sql)
    db.commit()

def setUpdateFlag(db):
    cur = db.cursor()
    cur.execute("update CarPrice set updated=0")
    db.commit()

def removeNotCar(db):
    cur = db.cursor()
    cur.execute("delete from CarPrice where updated=0")
    db.commit()
        


     
