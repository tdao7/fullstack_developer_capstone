from django.contrib import admin
from .models import CarMake, CarModel, Review


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ["id", "make", "name", "type", "year"]
    list_filter = ["make", "type"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "dealership", "name", "sentiment", "created_at"]
    list_filter = ["dealership", "sentiment"]
