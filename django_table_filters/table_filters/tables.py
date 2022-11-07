import inspect

from django.db.models import QuerySet

from django_tables2 import tables


class TableMetaclass(tables.DeclarativeColumnsMetaclass):
    def __new__(cls, name, bases, attrs):
        return tables.DeclarativeColumnsMetaclass.__new__(cls, name, bases, attrs)


class Table(tables.Table, metaclass=TableMetaclass):

    def __init__(self, *, request, data=None, table_filter=None, **kwargs):
        self.table_filter = table_filter

        if table_filter is not None:
            self.table_filter_activation = True
            data = table_filter.filtered_data
        elif data is not None:
            self.table_filter_activation = False
        else:
            assert data is not None, f'in {type(self)}.__init__ one of parameters "data or table_filter" is required'

        super(Table, self).__init__(request=request, data=data, **kwargs)



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
