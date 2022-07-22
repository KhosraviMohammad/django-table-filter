class TableFilterOption:
    def __init__(self, *, options):
        pass


class TableFilterMetaclass(type):
    def __new__(cls, name, bases, attrs):
        return type.__new__(cls, name, bases, attrs)


class TableFilter(metaclass=TableFilterMetaclass):
    pass
