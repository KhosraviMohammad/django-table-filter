from django_tables2 import tables
import inspect


class TableMetaclass(tables.DeclarativeColumnsMetaclass):
    def __new__(cls, name, bases, attrs):
        return tables.DeclarativeColumnsMetaclass.__new__(cls, name, bases, attrs)


class Table(tables.Table, metaclass=TableMetaclass):

    def __init__(self, *args, table_filter_activation=False, request=None, **kwargs):
        table_kwargs = split_parms_function(super(Table, self).__init__, kwargs=kwargs)
        table_filter_kwargs = kwargs
        if table_filter_activation and hasattr(Table, 'table_filter'):
            if request is not None:
                raise ValueError(f'table_filter is true, so request parm can not be None in {self}.__init__')
            # if not isinstance(data, QuerySet):
            #     raise TypeError(f'table_filter is true, so the data parm in {self} must be instance of QuerySet')
            obj = self.table_filter(request, **table_filter_kwargs)
            self.table_filter_obj = obj
            super(Table, self).__init__(*args, **table_kwargs)
        else:
            super(Table, self).__init__(*args, **table_kwargs)


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

