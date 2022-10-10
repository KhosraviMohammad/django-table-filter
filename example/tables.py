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
        columns = '__ALL__'
