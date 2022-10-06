from .tables import Table
from .column_filters import ColumnFilter
from django.contrib.admin import utils
from django.core import exceptions
from django_filters import filterset
from . import conf


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
        if hasattr(self.table.Meta, 'model'):
            self.model = getattr(self.table.Meta, 'model')
        else:
            AttributeError(f'{class_name}.Meta.table = "{self.table}" without model')
        self.columns = getattr(options, 'columns', [])
        self.exclude = getattr(options, 'exclude', [])
        if self.columns == '__ALL__':
            self.columns = []
            self.set__ALL__(self.columns, self.table.base_columns, self.model)
        if self.exclude == '__ALL__':
            self.exclude = []
            self.set__ALL__(self.exclude, self.table.base_columns, self.model)
        self._check_column_and_exclude(self.columns, self.exclude, self.table, class_name)

    def set__ALL__(self, list_object: list, base_columns, model):
        """
        it finds all possible columns in base_columns and set them to list_object
        possible column is the column in table that exist as field in model
        possible column:
            it is 'table.name_column == model.name_field'


        :param list_object:
        :param base_columns:
        :param model:
        :return:
        """
        try:
            for name, column in base_columns.items():
                fields = utils.get_fields_from_path(model, name)
                if len(fields) > 0:
                    list_object.append(name)
        except exceptions.FieldDoesNotExist:
            pass

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
            if table.base_columns.get(item) is None:
                raise AttributeError(f'defined column "{item}" in {class_name}.Meta.columns without column in {table}')

        for item in exclude:
            if table.base_columns.get(item) is None:
                raise AttributeError(f'excluded column "{item}" in {class_name}.Meta.exclude without column in {table}')

    def _check_types(self, options, class_name):
        """
        Check class Meta attributes to prevent common mistakes.
        """
        if options is None:
            return None

        checks = {
            (tuple, list, set, str): ["columns", "exclude"],
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
        if attrs['__module__'] + '.' + name == 'django_table_filters.table_filters.table_filters.TableFilter':
            new_class = type.__new__(cls, name, bases, attrs)
            return new_class
        if attrs.get('Meta') is None:
            raise AttributeError(f'{name} without Meta class')
        attrs['_meta'] = opt = TableFilterOption(options=attrs.get('Meta'), class_name=name)
        cls.set_base_column_filters(attrs)
        base_column_filters = attrs['base_column_filters']
        cls.check_column_filters(base_column_filters, opt.table)
        cls.add_column_filters(base_column_filters, opt.columns, opt.table, opt.model)
        attrs['ColumnFilterSets'] = cls.generate_ColumnFilterSets(base_column_filters, opt.model)
        # it givs the class of TableFilter as object
        # then, assigned output to new class variable
        new_class = type.__new__(cls, name, bases, attrs)
        # this gets two params, one is Table class and another one is TableFilter Class
        # after it sets TableFilter to Table
        Table.set_table_filter(opt.table, new_class)
        return new_class

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
        for name, column_filter in base_column_filters.items():
            if table.base_columns.get(name) is None:
                raise AttributeError(f'defined column filter "{name}" without column in {table}')

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
            column_filter = conf.generate_column_filter(column=table.base_columns[column], table=table, model=model,
                                                        split_column_names=split_column_names,
                                                        name_and_fields=name_and_fields,
                                                        fields_and_models=fields_and_models)
            if base_column_filters.get(column) is None:
                base_column_filters.update({column: column_filter})

    @staticmethod
    def generate_ColumnFilterSets(base_column_filters, model):
        """
        generate ColumnFilterSet for each base_column_filters which is FilterSet

        :param base_column_filters:
        :param model:
        :return ColumnFilterSet:
        """

        ColumnFilterSets = {}
        for key, value in base_column_filters.items():
            meta = type(str("Meta"), (object,), {"model": model, "fields": []})
            attrs = {"Meta": meta}
            attrs.update(value.filters)
            ColumnFilterSet = type(str("%s_ColumnFilterSet" % key), (filterset.FilterSet,), attrs)
            ColumnFilterSets.update({key: ColumnFilterSet})
        return ColumnFilterSets


class TableFilter(metaclass=TableFilterMetaclass):

    def __init__(self, *, data, request, ):
        self.data = data
        self._filtered_data, self.column_filter_sets = self.filter_data(ColumnFilterSets=self.ColumnFilterSets,
                                                                        request=request,
                                                                        data=data)

    def filter_data(self, *, ColumnFilterSets, request, data):
        """
        it filters data

        :param ColumnFilterSets:
        :param request:
        :param data:
        :return data:
        :return column_filter_sets:
        """
        column_filter_sets = {}
        for name, ColumnFilterSet in ColumnFilterSets.items():
            column_filter_set = ColumnFilterSet(request.GET, queryset=data)
            data = column_filter_set.qs
            column_filter_sets.update({name: column_filter_set})
        return data, column_filter_sets

    @property
    def filtered_data(self):
        return self._filtered_data
