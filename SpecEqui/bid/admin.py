from django.contrib import admin
from .models import Equipment, Manufacturer, Tag, EquipmentDetail


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'manufacturer', 'price_per_hour', 'status', 'time_create')
    list_filter = ('status', 'time_create', 'manufacturer', 'tags')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(EquipmentDetail)
class EquipmentDetailAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'engine', 'transmission', 'mileage')
    search_fields = ('equipment__title', 'engine', 'transmission')
