from django import template
from django.template import Node, Context

register = template.Library()


class RenderTableFilterNode(Node):

    def __init__(self, table, column, template_name):
        super().__init__()

        self.table = table
        self.column = column
        self.template_name = template_name

    def render(self, context):
        request = context.get("request")
        user = context.get("user")
        table = self.table.resolve(context)
        table_filter = table.table_filter
        column = self.column.resolve(context)
        column_filter_set = table_filter.column_filter_sets.get(column.name)
        if column_filter_set is None:
            return ''
        form = column_filter_set.form
        template_name = self.template_name.resolve(context)
        template = context.template.engine.get_template(template_name)

        new_context = Context(
            {
                'form': form,
                'table': table,
                'column': column,
                'table_filter': table_filter,
                'column_filter_set': column_filter_set,
                'request': request,
                'user': user,
            },
            autoescape=context.autoescape
        )
        return template.render(new_context)


@register.tag
def render_table_filter(parser, token):
    """
    Render a HTML table_filter.

    the tag must given table ,column ,and template_name

    """
    bits = token.split_contents()
    bits.pop(0)

    table = parser.compile_filter(bits.pop(0))
    column = parser.compile_filter(bits.pop(0))
    template_name = parser.compile_filter(bits.pop(0))

    return RenderTableFilterNode(table, column, template_name)
