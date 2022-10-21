from django_table_filters.table_filters import Table, TableFilter, ColumnFilter, Column
from example import models


class LibraryTable(Table):
    class Meta:
        model = models.Library
        template_name = 'django_table_filter/table/bootstrap4.html'
        fields = ['name', 'location', 'users']


class LibraryTableFilter(TableFilter):
    class Meta:
        table = LibraryTable
        columns = ['name']


class BookTable(Table):
    class Meta:
        model = models.Book
        template_name = 'django_table_filter/table/bootstrap4.html'
        fields = ['name', 'code', 'Registration_Date', 'price', 'library', 'library__location', 'library__users', 'library__users__username']


class BookTableFilter(TableFilter):
    class Meta:
        table = BookTable
        columns = ['name', 'code', 'Registration_Date', 'price', 'library', 'library__location', 'library__users',]
