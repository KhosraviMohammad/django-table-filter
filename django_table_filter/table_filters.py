from .tables import Table
from .column_filters import ColumnFilter
from django.contrib.admin import utils


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
        if self.columns == '__ALL__':
            self.columns = []
            for key, value in self.table.base_columns.items():
                self.columns.append(key)
        if self.exclude == '__ALL__':
            self.exclude = []
            for key, value in self.table.base_columns.items():
                self.exclude.append(key)
        self._check_column_and_exclude(self.columns, self.exclude, self.table, class_name)

    def _check_column_and_exclude(self, columns, exclude, table, class_name):
        """
        it checks column and exclude with column in table
        if required column does not exist in table then it raises AttributeError

        :param columns:
        :param exclude:
        :param table:
        :param class_name:
        :return:
        """

        for item in columns:
            if table.base_column_filters.get(item) is None:
                raise AttributeError(f'defined column "{item}" in {class_name}.Meta.columns without column in {table}')

        for item in exclude:
            if table.base_column_filters.get(item) is None:
                raise AttributeError(f'excluded column "{item}" in {class_name}.Meta.exclude without column in {table}')

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

    @staticmethod
    def add_column_filters(base_column_filters, columns, table, model):
        """
        it makes columnFilter ready for columns from params then add them to base_column_filters

        :param base_column_filters:
        :param columns:
        :param table:
        :param model:
        :return:
        """
        for column in columns:
            fields = utils.get_fields_from_path(model, column)
            name_and_fields = {}
            fields_and_models = {}
            split_column_names = tuple(column.split(utils.LOOKUP_SEP))
            for number, field in enumerate(fields):
                name_and_fields.update({split_column_names[number]: field})
                try:
                    fields_and_models.update({field: utils.get_model_from_relation(field)})
                except utils.NotRelationField:
                    pass
            column_filter = generate_column_filter(column=table.base_columns[column], table=table, model=model,
                                                   split_column_names=split_column_names,
                                                   name_and_fields=name_and_fields, fields_and_models=fields_and_models)
            base_column_filters.update({column:column_filter})


class TableFilter(metaclass=TableFilterMetaclass):
    pass


def generate_column_filter(*, column, table, model, split_column_names, name_and_fields, fields_and_models):
    ...
