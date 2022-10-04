from django_table_filters.table_filters import Table, TableFilter, ColumnFilter, Column
from example import models


class LibraryTable(Table):
    class Meta:
        model = models.Library
        template_name = 'django_tables2/bootstrap4.html'
        fields = ['name', 'location', 'users']


class LibraryTableFilter(TableFilter):
    class Meta:
        table = LibraryTable
