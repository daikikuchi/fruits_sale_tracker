# encoding=utf8
from __future__ import unicode_literals
import csv
import codecs
from datetime import datetime
from datetime import date
from itertools import groupby
from collections import defaultdict, OrderedDict
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from django.urls import reverse_lazy
from django import http, urls
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import Sum, Count
from fruitsales.models import FruitInfo, FruitSalesInfo
from fruitsales.forms import FruitCreateForm, FruitSalesForm

# Create your views here.


class MainView(LoginRequiredMixin, TemplateView):
    login_url = '/'
    template_name = 'main.html'


# 果物マスター
class FruitListView(LoginRequiredMixin, ListView):
    login_url = '/'
    context_object_name = 'fruits'
    model = FruitInfo
    template_name = "fruitsales/fruit_admin_list.html"

    def get_queryset(self):
        return FruitInfo.objects.order_by('-id')


class CreateFruitInfoView(LoginRequiredMixin, CreateView):
    login_url = '/'
    form_class = FruitCreateForm
    model = FruitInfo
    template_name = "fruitsales/fruit_form.html"


class FruitInfoUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = 'fruitsales/fruit_admin_list.html'
    form_class = FruitCreateForm
    model = FruitInfo
    template_name = "fruitsales/fruit_form.html"


class FruitInfoDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/'
    model = FruitInfo
    success_url = reverse_lazy('fruit_admin_list')


# 販売情報管理
class FruitSalesListView(LoginRequiredMixin, ListView):
    login_url = '/'
    context_object_name = 'fruits_sales'
    model = FruitSalesInfo
    template_name = "fruitsales/fruitsales_admin_list.html"

    def get_queryset(self):
        return FruitSalesInfo.objects.order_by('-sold_date')


class CreateFruitSalesView(LoginRequiredMixin, CreateView):
    login_url = '/'
    form_class = FruitSalesForm
    model = FruitSalesInfo
    template_name = "fruitsales/fruitsales_form.html"


class FruitSalesInfoUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = 'fruitsales/fruitsales_admin_list.html'
    form_class = FruitSalesForm
    model = FruitSalesInfo
    template_name = "fruitsales/fruitsales_form.html"


class FruitSalesDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/'
    model = FruitSalesInfo
    success_url = reverse_lazy('fruitsales_admin_list')


# 販売統計情報
@login_required(login_url='/')
def sale_stats(request):
    if FruitSalesInfo.objects.all().count() > 0:
        month_group = {}
        day_group = {}

        #　月別金額の計算

        three_months = FruitSalesInfo.objects.annotate(
            month=TruncMonth('sold_date')).values('month').order_by(
                '-month').distinct()[:3]

        three_months_rows = FruitSalesInfo.objects.annotate(
            month=TruncMonth('sold_date')).filter(month__gte=three_months[
                len(three_months) - 1]['month']).order_by(
                    '-sold_date', 'fruitinfo__id')

        grand_total_monthly = get_total_price(three_months_rows, "month")

        monthly_details = get_details(three_months_rows, "month")

        month_group = OrderedDict(
            sorted(monthly_details.items(), reverse=True))

        print month_group
        # #　日別金額の計算
        trunc_day = FruitSalesInfo.objects.annotate(day=TruncDate('sold_date'))

        three_days = trunc_day.values('day').order_by('-day').distinct()[:3]
        three_days_rows = trunc_day.filter(
            day__gte=three_days[len(three_days) - 1]['day']).order_by(
                '-sold_date', 'fruitinfo__id')
        daily_details = get_details(three_days_rows, "day")
        day_group = OrderedDict(sorted(daily_details.items(), reverse=True))

    #　累計金額
    sales_total = FruitSalesInfo.objects.all().aggregate(Sum('total_price'))

    return render(
        request, "fruitsales/fruitsales_admin_stats.html", {
            'month_group': month_group,
            'day_group': day_group,
            'sales_total': sales_total,
        })


def get_total_price(data, mode):
    result = {}
    for i in data:
        if mode == "month":
            period = i.sold_date.strftime("%Y-%m")
        else:
            period = i.sold_date.strftime("%Y-%m-%d")
        if period in result.keys():
            result[period] = result[period] + i.total_price
        else:
            result[period] = i.total_price
    return result


def get_details(data, mode):
    total_price_result = get_total_price(data, mode)
    result = {}
    for i in data:
        fruit = i.fruitinfo.name

        if mode == "month":
            period = i.sold_date.strftime("%Y-%m")
        else:
            period = i.sold_date.strftime("%Y-%m-%d")

        if period in result.keys():
            if fruit == result.get(period)[0][0]:
                result.get(period)[0] = (
                    result.get(period)[0][0],
                    result.get(period)[0][1] + i.total_price,
                    result.get(period)[0][2] + i.number)

            else:
                result[period].append((fruit, i.total_price, i.number))
        else:
            result[period] = [(fruit, i.total_price, i.number)]
    # appending grand total at the end
    for j in result:
        result[j].append((total_price_result.get(j)))
    print result
    return result


# CSV


def upload_csv(request):
    failures = []
    if request.POST and request.FILES:
        csvfile = request.FILES['csv']
        dialect = csv.Sniffer().sniff(
            codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        reader = csv.reader(
            codecs.EncodedFile(csvfile, "utf-8"),
            delimiter=str(u','),
            dialect=dialect)
        for row in reader:
            if len(row) == 4:
                try:
                    fruit = FruitInfo.objects.filter(name=row[0]).first()
                    # date format can be yyyy-mm-dd hh:mm or yyyy-mm-dd
                    if len(row[3]) == 10:  # yyyy-mm-dd
                        date = datetime.strptime(row[3], "%Y-%m-%d")
                    elif len(row[3]) == 16:  # yyyy-mm-dd hh:mm
                        date = datetime.strptime(row[3], "%Y-%m-%d %H:%M")
                    FruitSalesInfo.objects.get_or_create(
                        fruitinfo=fruit,
                        number=int(row[1]),
                        total_price=int(row[2]),
                        sold_date=date)
                except Exception:
                    message = "Error processing csv file"

    return http.HttpResponseRedirect(urls.reverse('fruitsales_admin_list'))
