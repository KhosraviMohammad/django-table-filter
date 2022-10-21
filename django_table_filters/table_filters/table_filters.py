from collections import OrderedDict

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
        # Options is got from Table.Filter.Meta that given to this method to check type of
        # specific attributes which are required as option for Table.Filter._meta
        self._check_types(options=options, class_name=class_name)

        self.table = getattr(options, 'table', None)
        if self.table is not None:
            self.model = getattr(self.table._meta, 'model', None)
        else:
            self.model = None

        self.columns = getattr(options, 'columns', [])
        self.exclude = getattr(options, 'exclude', [])

    def _check_types(self, *, options, class_name):
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
    def __new__(mcs, name, bases, attrs):
        attrs['_meta'] = opt = TableFilterOption(options=attrs.get('Meta'), class_name=name)
        attrs["declared_column_filters"] = declared_column_filters = mcs.get_declared_column_filters(
            bases=bases, attrs=attrs)
        mcs.check_declared_column_filters(declared_column_filters=declared_column_filters, table=opt.table)
        attrs["generated_column_filters"] = generated_column_filters = mcs.get_generated_column_filters(
            columns=opt.columns, exclude=opt.exclude, model=opt.model, table=opt.table, class_name=name)
        attrs["base_column_filters"] = base_column_filters = mcs.get_base_column_filters(
            declared_column_filters=declared_column_filters, generated_column_filters=generated_column_filters)
        attrs['ColumnFilterSets'] = mcs.generate_ColumnFilterSets(base_column_filters=base_column_filters, model=opt.model)

        # it givs the class of TableFilter as object
        # then, assigned output to new class variable
        new_class = type.__new__(mcs, name, bases, attrs)
        # this gets two params, one is Table class and another one is TableFilter Class
        # after it sets TableFilter to Table
        Table.set_table_filter(opt.table, new_class)

        return new_class

    def get_declared_column_filters(cls, *, bases, attrs):
        '''
        this method finds column_filters which are declared in TableFilter class

        :param bases:
        :param attrs:
        :return:
        '''

        column_filters = [
            (column_filter_name, attrs.pop(column_filter_name))
            for column_filter_name, obj in list(attrs.items())
            if isinstance(obj, ColumnFilter)
        ]

        for column_filter_name, column_filter in column_filters:
            if getattr(column_filter, "column_filter_name", None) is None:
                column_filter.column_filter_name = column_filter_name

        known = set(attrs)

        def visit(name):
            known.add(name)
            return name

        base_column_filters = [
            (visit(column_filter_name), column_filter)
            for base in bases
            if hasattr(base, "declared_column_filters")
            for column_filter_name, column_filter in base.declared_column_filters.items()
            if column_filter_name not in known
        ]

        return OrderedDict(base_column_filters + column_filters)

    def get_base_column_filters(cls, *, declared_column_filters, generated_column_filters):
        """
        it connects declared_column_filters and generated_column_filters at base_column_filters and return it

        :param attrs:
        :return:
        """
        base_column_filters = OrderedDict()
        base_column_filters.update(declared_column_filters)
        base_column_filters.update(generated_column_filters)
        return base_column_filters

    def check_declared_column_filters(cls, *, declared_column_filters, table):
        """
        it checks column filter with column in table

        :param declared_column_filters:
        :param table:
        :return:
        """
        for name, column_filter in declared_column_filters.items():
            if table.base_columns.get(name) is None:
                raise AttributeError(f'defined column filter "{name}" without defining this column "{name}" in {table}')

    def get_generated_column_filters(cls, *, columns, exclude, table, model, class_name):
        """
        it makes columnFilter ready for columns from params then return

        :param columns:
        :param exclude:
        :param table:
        :param model:
        :param class_name:
        :return:
        """

        if table is None:
            raise NotImplementedError(f'{class_name}.Meta.columns or {class_name}.Meta.columns exclude'
                                      f' without {class_name}.Meta.table')
        elif model is None:
            raise NotImplementedError(f'{class_name}.Meta.table does not have model')

        cls._check_column_and_exclude(columns=columns, exclude=exclude, table=table, class_name=class_name)

        ALL_COLUMNS = '__ALL__'

        if len(exclude) != 0 and len(columns) != 0:
            columns = ALL_COLUMNS

        if columns == ALL_COLUMNS:
            columns = cls.set__ALL__(list_name=[], table_base_columns=table.base_columns, model=model)

        column_filters = OrderedDict()

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
            column_filter = conf.GENERATE_COLUMN_FILTER(column=table.base_columns[column], table=table, model=model,
                                                        split_column_names=split_column_names,
                                                        name_and_fields=name_and_fields,
                                                        fields_and_models=fields_and_models)
            column_filters.update({column: column_filter})
        return column_filters

    def set__ALL__(cls, *, list_name: list, table_base_columns, model):
        """
        it finds all possible columns in base_columns and set them to list_object
        possible column is the column in table that exist as field in model
        possible column:
            it is 'table.name_column == model.name_field'


        :param list_name:
        :param table_base_columns:
        :param model:
        :return:
        """
        try:
            for name, column in table_base_columns.items():
                fields = utils.get_fields_from_path(model, name)
                if len(fields) > 0:
                    list_name.append(name)
        except exceptions.FieldDoesNotExist:
            pass

        return list_name

    def _check_column_and_exclude(cls, *, columns, exclude, table, class_name):
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


    def generate_ColumnFilterSets(cls, *, base_column_filters, model):
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
