import inspect

from django.db.models import QuerySet

from django_tables2 import tables


class TableMetaclass(tables.DeclarativeColumnsMetaclass):
    def __new__(cls, name, bases, attrs):
        return tables.DeclarativeColumnsMetaclass.__new__(cls, name, bases, attrs)


class Table(tables.Table, metaclass=TableMetaclass):

    def __init__(self, *, request, data, table_filter_activation=False, **kwargs):
        table_kwargs = split_prams_function(super(Table, self).__init__, kwargs=kwargs)
        table_filter_kwargs = kwargs
        table_kwargs['data'] = data
        self.request = request
        if table_filter_activation and hasattr(type(self), 'TableFilter'):
            if not isinstance(data, QuerySet):
                raise TypeError(f'table_filter is true, so the data parm in {self} must be instance of QuerySet')
            table_filter = self.TableFilter(data=data, request=request, **table_filter_kwargs)
            self.table_filter = table_filter
            table_kwargs['data'] = table_filter.filtered_data
            super(Table, self).__init__(**table_kwargs)
        else:
            super(Table, self).__init__(**table_kwargs)

    @staticmethod
    def set_table_filter(table, table_filter):
        """
        it sets table_filter as attribute to table.table_filter

        :param table:
        :param table_filter:
        :return:
        """
        table.TableFilter = table_filter


def split_prams_function(func, kwargs: dict):
    """
    it compares func kwargs with kwargs after, if some items are appeared that are the same in both,
    then it outs that item in kwargs, puts to another dic varible, and return it

    :param func:
    :param kwargs:
    :return:
    """
    argspec = inspect.getfullargspec(func=func)
    splitted_kwargs = {}
    if not (len(kwargs) == 0) and not (len(argspec.kwonlyargs) == 0):
        if len(argspec.kwonlyargs) < len(kwargs):
            for key in argspec.kwonlyargs:
                splitted_kwargs[key] = kwargs.pop(key, argspec.kwonlydefaults[key])
                if len(kwargs) == 0:
                    break
        else:
            kwonlydefaults = dict(argspec.kwonlydefaults)
            for key in list(kwargs.keys()):
                if key in kwonlydefaults:
                    splitted_kwargs[key] = kwargs.pop(key, kwonlydefaults.pop(key))
                    if len(argspec.kwonlydefaults) == 0:
                        break
    if not (len(kwargs) == 0) and not (len(argspec.args) == 0):
        if len(argspec.args) < len(kwargs):
            for key in argspec.args:
                if key in kwargs:
                    splitted_kwargs[key] = kwargs.pop(key)
                    if len(kwargs) == 0:
                        break
        else:
            for key in list(kwargs.keys()):
                index = argspec.args.index(key)
                if not (index == -1):
                    splitted_kwargs[key] = kwargs.pop(key)
                    if len(kwargs) == 0:
                        break

    return splitted_kwargs
