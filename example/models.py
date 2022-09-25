from re import T
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class BasicModle(models.Model):
    class Meta:
        abstract = True


class Library(BasicModle):
    name = models.CharField(max_length=200)
    location = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User)

class Book(BasicModle):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    Registration_Date = models.DateTimeField()
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    






