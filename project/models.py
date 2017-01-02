from __future__ import unicode_literals

from django.db import models


class Car(models.Model):
    car_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    year = models.IntegerField()
    price = models.IntegerField()
    prev_price = models.IntegerField()
    updated_on = models.DateField(auto_now=True)
    updated = models.IntegerField(default=1)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'CarPrice'


class Make(models.Model):
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)

    def __unicode__(self):
        return self.alias

    class Meta:
        ordering = ('name',)


class Model(models.Model):
    make = models.ForeignKey(Make)
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)

    def __unicode__(self):
        return "{} - {} - {}".format(self.make.alias, self.alias, self.name)

    class Meta:
        ordering = ('make__alias', 'name')


class YearFilter(models.Model):
    model = models.ForeignKey(Model)
    from_year = models.IntegerField('From')
    to_year = models.IntegerField('To')

    def __unicode__(self):
        return "{} : {}-{}".format(self.model.alias, self.from_year, self.to_year)
