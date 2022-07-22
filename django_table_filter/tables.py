from django_tables2 import tables


class TableMetaclass(tables.DeclarativeColumnsMetaclass):
    def __new__(cls, name, bases, attrs):
        return tables.DeclarativeColumnsMetaclass(cls, name, bases, attrs)


class Table(tables.Table, metaclass=TableMetaclass):
    
    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
