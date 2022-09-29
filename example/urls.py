from django.urls import path
from . import views

app_name = 'example'

urlpatterns = [
    path('', views.library_view, name='library_view')
]
