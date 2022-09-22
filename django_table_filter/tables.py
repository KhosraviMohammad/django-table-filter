from django_tables2 import tables
import inspect


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


def split_parms_function(func, kwargs: dict):
    """
    it compares func kwargs with kwargs after, if some items are appeared that are the same in both,
    then it outs that item in kwargs, puts to another dic varible, and return it

    :param func:
    :param kwargs:
    :return:
    """
    argspec = inspect.getfullargspec(func=func)
    splited_kwargs = {}
    for value in argspec.kwonlyargs:
        splited_kwargs[value] = kwargs.pop(value, argspec.kwonlydefaults[value])
    return splited_kwargs

