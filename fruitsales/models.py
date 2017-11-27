# encoding=utf8
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import Sum, Count
from collections import defaultdict, OrderedDict

# Create your models here.


class FruitInfo(models.Model):
    name = models.CharField(max_length=175, unique=True)
    price = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('fruit_admin_list')

    def __unicode__(self):
        return self.name


class FruitSalesInfo(models.Model):

    number = models.PositiveIntegerField(default=0)
    sold_date = models.DateTimeField(auto_now_add=False, blank=False)
    fruitinfo = models.ForeignKey(FruitInfo, related_name='fruits')
    total_price = models.PositiveIntegerField(default=0)

    def save(self, **kwargs):
        self.total_price = self.fruitinfo.price * self.number
        super(FruitSalesInfo, self).save()

    def get_absolute_url(self):
        return reverse('fruitsales_admin_list')
