from .tables import Table


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
        return type.__new__(cls, name, bases, attrs)


class TableFilter(metaclass=TableFilterMetaclass):
    pass
