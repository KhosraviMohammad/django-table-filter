from django_table_filters.table_filters import Table, TableFilter, ColumnFilter, Column
from example import models
from django_filters import filters
from django import forms


class LibraryTable(Table):
    class Meta:
        model = models.Library
        template_name = 'django_table_filter/table/bootstrap4.html'
        fields = ['name', 'location', 'users']


class LibraryTableFilter(TableFilter):
    class Meta:
        table = LibraryTable
        exclude = ['location']


class BookTable(Table):
    class Meta:
        model = models.Book
        template_name = 'django_table_filter/table/bootstrap4.html'
        fields = ['name', 'code', 'Registration_Date', 'price', 'library', 'library__location', 'library__users', 'library__users__username']


class BookTableFilter(TableFilter):
    price = ColumnFilter({
        'price_from': filters.NumberFilter(field_name='price', lookup_expr='gte', widget=forms.NumberInput(attrs={'class': 'form-control input-filter', 'placeholder': 'from'})),
        'price_to': filters.NumberFilter(field_name='price', lookup_expr='lte', widget=forms.NumberInput(attrs={'class': 'form-control input-filter', 'placeholder': 'to'})),
    })

    class Meta:
        table = BookTable
        columns = ['name', 'code', 'Registration_Date', 'library', 'library__location', 'library__users', ]
