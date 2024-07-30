import django_filters
from .models import Projects
from django.contrib.auth.models import User
from django_filters import CharFilter
from django import forms

class OrderFilter(django_filters.FilterSet):
    creator = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    status = django_filters.ChoiceFilter(choices=Projects.STATUS_CHOICES)
    name = CharFilter(field_name='name', lookup_expr="icontains")
    title = CharFilter(field_name='title', lookup_expr="icontains")
    occupation = django_filters.ChoiceFilter(choices=Projects.OCCUPATION_CHOICES)
    postgraduate_type = django_filters.ChoiceFilter(choices=Projects.POSTGRADUATE_CHOICES)
    date = django_filters.DateFilter(field_name='date', lookup_expr='date__exact', widget=forms.DateInput(attrs={'type': 'date'})) # Add this line to filter by date

    class Meta:
        model = Projects
        fields = ['name', 'title', 'date', 'status', 'creator', 'occupation', 'postgraduate_type']

