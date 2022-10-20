from django.db import models
from django_filters import filters
from .column_filters import ColumnFilter
from django import forms


def generate_column_filter(*, column, table, model, split_column_names, name_and_fields, fields_and_models):
    last_field_name = split_column_names[len(split_column_names) - 1]
    last_field = name_and_fields[last_field_name]
    filter_accessor = column.accessor
    column_filter = ColumnFilter()
    if last_field.choices is not None:
        column_filter = ColumnFilter({filter_accessor: filters.ChoiceFilter(choices=last_field.choices, widget=forms.TextInput(attrs={'class': 'form-control input-filter'}))})
    elif isinstance(last_field, models.ManyToManyField):
        last_model = fields_and_models[last_field]
        column_filter = ColumnFilter({filter_accessor: filters.ModelMultipleChoiceFilter(queryset=last_model.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control input-filter'}))})
    elif isinstance(last_field, models.ForeignKey):
        last_model = fields_and_models[last_field]
        column_filter = ColumnFilter({filter_accessor: filters.ModelChoiceFilter(queryset=last_model.objects.all(), widget=forms.Select(attrs={'class': 'form-control input-filter'}))})
    elif isinstance(last_field, models.CharField):
        column_filter = ColumnFilter({filter_accessor: filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control input-filter'}))})
    elif isinstance(last_field, models.DateTimeField):
        filter_from = filters.DateTimeFilter(field_name=filter_accessor, lookup_expr='gte', widget=forms.DateTimeInput(attrs={'class': 'form-control input-filter', 'placeholder': 'from'}))
        filter_to = filters.DateTimeFilter(field_name=filter_accessor, lookup_expr='lte', widget=forms.DateTimeInput(attrs={'class': 'form-control input-filter', 'placeholder': 'to'}))
        column_filter = ColumnFilter({'date_from': filter_from, 'data_to': filter_to})
    elif isinstance(last_field, models.DecimalField):
        filter_from = filters.NumberFilter(field_name=filter_accessor, lookup_expr='gte', widget=forms.NumberInput(attrs={'class': 'form-control input-filter', 'placeholder': 'from'}))
        filter_to = filters.NumberFilter(field_name=filter_accessor, lookup_expr='lte', widget=forms.NumberInput(attrs={'class': 'form-control input-filter', 'placeholder': 'to'}))
        column_filter = ColumnFilter({'number_from': filter_from, 'number_to': filter_to})
    elif isinstance(last_field, models.TextField):
        text_filter = filters.CharFilter(field_name=filter_accessor, lookup_expr='icontains', widget=forms.Textarea(attrs={'class': 'form-control input-filter'}))
        column_filter = ColumnFilter({'text_filter': text_filter})
    return column_filter
