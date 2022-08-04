from .tables import Table
from .column_filters import ColumnFilter


class TableFilterOption:
    """
    it is TableFilter option from TableFilter.Meta

    TableFilter.Meta --> TableFilter._meta
    _meta is option for TableFilter
    """

    def __init__(self, *, options, class_name):
        if not hasattr(options, 'table'):
            raise AttributeError(f'{class_name}.Meta without table')
        self._check_types(options, class_name)

        self.table = getattr(options, 'table')
        self.columns = getattr(options, 'columns', [])
        self.exclude = getattr(options, 'exclude', [])

    def _check_types(self, options, class_name):
        """
        Check class Meta attributes to prevent common mistakes.
        """
        if options is None:
            return None

        checks = {
            (tuple, list, set): ["columns", "exclude"],
            (type(Table),): ["table"],
        }

        for types, keys in checks.items():
            for key in keys:
                value = getattr(options, key, None)
                if value is not None and not isinstance(value, types):
                    expression = "{}.{} = {}".format(class_name, key, value.__repr__())

                    raise TypeError(
                        "{} (type {}), but type must be one of ({})".format(
                            expression, type(value).__name__, ", ".join([t.__name__ for t in types])
                        )
                    )


class TableFilterMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if attrs.get('Meta') is None:
            raise AttributeError(f'{name} without Meta class')
        attrs['_meta'] = opt = TableFilterOption(options=attrs.get('Meta'), class_name=name)
        cls.set_base_column_filters(attrs)
        base_column_filters = attrs['base_column_filters']
        cls.check_column_filters(base_column_filters, opt.table)
        return type.__new__(cls, name, bases, attrs)

    @staticmethod
    def set_base_column_filters(attrs):
        """
        it finds ColumnFilter instance and sets them to "base_column_filters"

        :param attrs:
        :return:
        """
        base_column_filters = {}
        for key, value in attrs.items():
            if isinstance(value, ColumnFilter):
                base_column_filters[key] = value
                del attrs[key]
        attrs['base_column_filters'] = base_column_filters

    @staticmethod
    def check_column_filters(base_column_filters, table):
        """
        it checks column filter with column in table

        :param base_column_filters:
        :param table:
        :return:
        """
        for key, value in base_column_filters.items():
            if table.base_columns.get(key) is None:
                raise AttributeError(f'defined column filter "{key}" without column in {table}')


class TableFilter(metaclass=TableFilterMetaclass):
    pass
