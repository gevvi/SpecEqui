from django.contrib import admin
from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_per_hour', 'status', 'time_create')
    list_filter = ('status', 'time_create')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}
