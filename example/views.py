from django.shortcuts import render
from .tables import LibraryTable, BookTable, LibraryTableFilter, BookTableFilter
from . import models


# Create your views here.

def library_view(request):
    library_qs = models.Library.objects.prefetch_related('users').all()
    library_table_filter = BookTableFilter(request=request, data=library_qs)
    library_table = LibraryTable(request=request, table_filter=library_table_filter)
    context = {
        'table': library_table,
    }
    return render(request, template_name='example/library.html', context=context)


def book_view(request):
    book_qs = models.Book.objects.select_related('library').all()
    book_table_filter = BookTableFilter(request=request, data=book_qs)
    book_table = BookTable(request=request, table_filter=book_table_filter)
    context = {
        'table': book_table
    }
    return render(request, template_name='example/book.html', context=context)
