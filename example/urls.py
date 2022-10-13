from django.urls import path
from . import views

app_name = 'example'

urlpatterns = [
    path('library', views.library_view, name='library_view'),
    path('book', views.book_view, name='book_view'),
]
