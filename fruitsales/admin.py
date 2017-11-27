# encoding=utf8
from __future__ import unicode_literals
from django.contrib import admin
from fruitsales.models import FruitInfo, FruitSalesInfo

# Register your models here.
admin.site.register(FruitInfo)
admin.site.register(FruitSalesInfo)
