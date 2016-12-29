from django.shortcuts import render_to_response, redirect
from project.models import *
from django.template import RequestContext
from django.contrib.auth.models import *

from functools import wraps

import datetime
from django.http import HttpResponse

import json
from django.views.decorators.csrf import csrf_exempt
from allauth.socialaccount.models import SocialAccount

from django.db.models import Q, Avg, Count

from car_price import settings
from collections import OrderedDict

from django.template.defaultfilters import slugify

def main(request):
    country_label = settings.COUNTRY

    currency_label = settings.CURRENCY
    try:
        currency = currency_label[request.GET["currency"]]
    except:
        currency = currency_label["USD"]

    res = OrderedDict()
    names = Car.objects.values('name').distinct().order_by("name")

    for name in names:

        car_per_country = Car.objects.filter(name=name["name"]).values('country').annotate(davg=Avg('price'), pavg=Avg('prev_price'))
        
        temp_data = OrderedDict()
        temp_data["USA"], temp_data["UK"], temp_data["France"], temp_data["Germany"], temp_data["Italy"], temp_data["Spain"],temp_data["Switzerland"], = None, None,None, None,None, None,None
        
         
        for item in car_per_country:
            if item["country"] in temp_data.keys():
                item["davg"] *= currency["currency_rate"]
                item["pavg"] *= currency["currency_rate"]
                item["percent"] = (item["davg"] - item["pavg"]) * 100 / item["davg"]
                temp_data[item["country"]] = {"davg": int(item["davg"]), "pavg": int(item["pavg"]), "percent": item["percent"]}

        res[name["name"]] = temp_data
    chartData = getChartData(dict(), currency["currency_rate"], type)
    menu = getMenu()
    car_name = None

    return render_to_response('cars.html', locals(), context_instance=RequestContext(request))

def req_brand(request, car_name):
    country_label = settings.COUNTRY

    car_name = getNameFromSlug(car_name, "name")

    currency_label = settings.CURRENCY
    try:
        currency = currency_label[request.GET["currency"]]
    except:
        currency = currency_label["USD"]

    res = OrderedDict()
    brands = Car.objects.filter(name=car_name).values('brand').distinct().order_by("brand")

    for brand in brands:
        car_per_country = Car.objects.filter(name=car_name, brand=brand["brand"]).values('country').annotate(davg=Avg('price'), pavg=Avg('prev_price'))

        temp_data = OrderedDict()
        temp_data["USA"], temp_data["UK"], temp_data["France"], temp_data["Germany"], temp_data["Italy"], temp_data["Spain"],temp_data["Switzerland"], = None, None,None, None,None, None,None
        
         
        for item in car_per_country:
            if item["country"] in temp_data.keys():
                item["davg"] *= currency["currency_rate"]
                item["pavg"] *= currency["currency_rate"]
                item["percent"] = (item["davg"] - item["pavg"]) * 100 / item["davg"]
                temp_data[item["country"]] = {"davg": int(item["davg"]), "pavg": int(item["pavg"]), "percent": item["percent"]}

        res[brand["brand"]] = temp_data

    chartData = getChartData({"car_name": car_name}, currency["currency_rate"])
    menu = getMenu()

    return render_to_response('cars.html', locals(), context_instance=RequestContext(request))

def req_year(request, car_name, brand):
    country_label = settings.COUNTRY

    currency_label = settings.CURRENCY
    try:
        currency = currency_label[request.GET["currency"]]
    except:
        currency = currency_label["USD"]

    car_name = getNameFromSlug(car_name, "name")
    car_brand = getNameFromSlug(brand, "brand")
    brand = car_brand

    res = OrderedDict()
    years = Car.objects.filter(name=car_name, brand=brand).values('year').distinct().order_by("-year")

    for year in years:
        car_per_country = Car.objects.filter(name=car_name, brand=brand, year=year["year"]).values('country').annotate(davg=Avg('price'), pavg=Avg('prev_price'))

        temp_data = OrderedDict()
        temp_data["USA"], temp_data["UK"], temp_data["France"], temp_data["Germany"], temp_data["Italy"], temp_data["Spain"],temp_data["Switzerland"], = None, None,None, None,None, None,None
        
         
        for item in car_per_country:
            if item["country"] in temp_data.keys():
                item["davg"] *= currency["currency_rate"]
                item["pavg"] *= currency["currency_rate"]
                item["percent"] = (item["davg"] - item["pavg"]) * 100 / item["davg"]
                temp_data[item["country"]] = {"davg": int(item["davg"]), "pavg": int(item["pavg"]), "percent": item["percent"]}

        res[year["year"]] = temp_data

    chartData = getChartData({"car_name": car_name, "car_brand": car_brand}, currency["currency_rate"])
    menu = getMenu()

    return render_to_response('cars.html', locals(), context_instance=RequestContext(request))

def getMenu():
    names = Car.objects.values('name').annotate(count=Count('price')).order_by("name")

    res = OrderedDict()
    for name in names:
        res[name["name"]] = [name, Car.objects.filter(name=name["name"]).values('brand').annotate(count=Count('brand')).order_by("brand")]
    return res

def getChartData(param, currency_rate, type=None):
    # get chart data
    years = Car.objects.values('year').distinct()

    years = [item["year"] for item in years]
    years = sorted(years, key=int, reverse=False)
    years = [int(item) for item in years]

    chartData = []    

    if type != None:
        tp_chartData = OrderedDict()

        temp = Car.objects.all().values("year", "name").annotate(davg=Avg('price')).order_by("name")
        for item in temp:
            if item["name"] not in tp_chartData:
                tp_chartData[item["name"]] = []

            tp_chartData[item["name"]].append([float(item["year"]), item["davg"]])

    
        for name in tp_chartData:
            data = sorted(tp_chartData[name], key=getKey)
            chartData.append({"name": name, "data": data})


    if "car_brand" in param:
        temp = Car.objects.filter(name=param['car_name'], brand=param['car_brand']).values("year", "country").annotate(davg=Avg('price')).order_by("country")
    elif "car_name" in param:
        temp = Car.objects.filter(name=param['car_name']).values("year", "country") \
                           .annotate(davg=Avg('price')).order_by("country")
    else:
        temp = Car.objects.all().values("year", "country") \
                           .annotate(davg=Avg('price')).order_by("country")

    tp_chartDataForCountry = OrderedDict()
    for item in temp:
        if item["country"] not in tp_chartDataForCountry:
            tp_chartDataForCountry[item["country"]] = []

        tp_chartDataForCountry[item["country"]].append([float(item["year"]), item["davg"]])

    chartDataForCountry = []
    for name in tp_chartDataForCountry:
        data = sorted(tp_chartDataForCountry[name], key=getKey)
        chartDataForCountry.append({"name": name, "data": data})

    return [chartData, chartDataForCountry, years]


def getNameFromSlug(slug, type):
    if type == "name":
        names = Car.objects.values('name').distinct()
        names = {slugify(name["name"]):name["name"] for name in names}

        return names[slug]
    elif type == "brand":
        brands = Car.objects.values('brand').distinct()
        brands = {slugify(brand["brand"]):brand["brand"] for brand in brands}

        return brands[slug]


def getKey(item):
    return item[0]


