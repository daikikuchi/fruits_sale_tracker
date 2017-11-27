# encoding=utf8
from __future__ import unicode_literals
import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import views
from django.utils.translation import ugettext_lazy as _
from fruitsales.models import FruitInfo, FruitSalesInfo


class FruitCreateForm(forms.ModelForm):
    class Meta():
        model = FruitInfo
        fields = ('name', 'price')

        labels = {'name': _('名称'), 'price': _('単価')}

        widgets = {
            'name':
            forms.TextInput(attrs={
                'class': 'textinputclass'
            }),
            'price':
            forms.TextInput(attrs={
                'type': 'number',
                'class': 'textinputclass'
            }),
        }


class FruitSalesForm(forms.ModelForm):

    fruitinfo = forms.ModelChoiceField(
        queryset=FruitInfo.objects.all(), label='果物名')

    class Meta():
        model = FruitSalesInfo
        fields = ('fruitinfo', 'number', 'sold_date')

        labels = {'number': _('販売数'), 'sold_date': _('販売日')}

    widgets = {
        'number':
        forms.TextInput(attrs={
            'type': 'number',
            'class': 'textinputclass'
        }),
        'sold_date':
        forms.DateField(),
    }

    def clean_number(self):
        number = self.cleaned_data['number']
        if number < 1:
            raise forms.ValidationError("1以上の数値を入力してください。")
        return number

    def clean_sold_date(self):
        sold_date = self.cleaned_data['sold_date']
        if sold_date > datetime.datetime.today():
            raise forms.ValidationError("販売日を入力してください。")
        return sold_date
