from django_tables2 import tables


class TableMetaclass(tables.DeclarativeColumnsMetaclass):
    def __new__(cls, name, bases, attrs):
        return tables.DeclarativeColumnsMetaclass(cls, name, bases, attrs)


class Table(tables.Table, metaclass=TableMetaclass):

    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)

    @staticmethod
    def set_table_filter(table, table_filter):
        """
        it sets table_filter as attribute to table.table_filter

        :param table:
        :param table_filter:
        :return:
        """
        table.table_filter = table_filter
