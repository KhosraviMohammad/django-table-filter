from django.shortcuts import render
from .tables import LibraryTable, BookTable
from . import models


# Create your views here.

def library_view(request):
    library_qs = models.Library.objects.prefetch_related('users').all()
    table = LibraryTable(data=library_qs, table_filter_activation=True, request=request)
    context = {
        'table': table,
    }
    return render(request, template_name='example/library.html', context=context)


def book_view(request):
    book_qs = models.Book.objects.select_related('library').all()
    book_table = BookTable(data=book_qs, request=request, table_filter_activation=True)
    context = {
        'table': book_table
    }
    return render(request, template_name='example/book.html', context=context)
