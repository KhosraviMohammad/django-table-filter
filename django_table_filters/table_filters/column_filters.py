from django_filters.filters import Filter


class ColumnFilter:
    def __init__(self, filters=None):
        if isinstance(filters, dict):
            for filter in filters.values():
                if not isinstance(filter, Filter):
                    raise TypeError(f'In "filters" items must be instance of {Filter} class')
            self.filters = filters
        elif filters is None:
            self.filters = {}
        else:
            raise TypeError('Filters must be dictionary object')
