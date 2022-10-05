from django.db import models
from django_filters import filters
from .column_filters import ColumnFilter


def generate_column_filter(*, column, table, model, split_column_names, name_and_fields, fields_and_models):
    # if isinstance(split_column_names[len(name_and_fields) - 1], models.CharField):
    return ColumnFilter({split_column_names[0]: filters.CharFilter()})
    # return ColumnFilter()
