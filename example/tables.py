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
    name = ColumnFilter({
        'name': filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control input-filter bg-light'})),
    })
    price = ColumnFilter({
        'price_from': filters.NumberFilter(field_name='price', lookup_expr='gte', widget=forms.NumberInput(attrs={'class': 'form-control input-filter bg-light', 'placeholder': 'from'})),
        'price_to': filters.NumberFilter(field_name='price', lookup_expr='lte', widget=forms.NumberInput(attrs={'class': 'form-control input-filter bg-light', 'placeholder': 'to'})),
    })

    class Meta:
        table = BookTable
        columns = ['name', 'code', 'price', 'Registration_Date', 'library', 'library__location', 'library__users', ]
