from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.utils.html import mark_safe
from .models import Equipment, Manufacturer, Tag, EquipmentDetail


@admin.display(description="Краткое описание")
def brief_info(obj):
    return f"{(obj.description or '')[:40]}…" if obj.description and len(obj.description) > 40 else (obj.description or "—")


@admin.display(description="Цена с сервисом (₽)")
def price_with_fee(obj):
    if obj.price_per_hour is None:
        return "0.00"
    return f"{round(float(obj.price_per_hour) * 1.15, 2)}"


@admin.display(description='Превью изображения')
def image_preview(obj):
    if obj.image:
        return mark_safe(f"<img src='{obj.image.url}' style='max-height:200px; max-width:200px; border-radius: 4px;' />")
    return "(нет изображения)"


class PriceRangeFilter(SimpleListFilter):
    title = "Диапазон цены/час"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return [
            ("low", "До 1 000 ₽"),
            ("mid", "1 000–3 000 ₽"),
            ("high", "Более 3 000 ₽"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "low":
            return queryset.filter(price_per_hour__lt=1000)
        if value == "mid":
            return queryset.filter(price_per_hour__gte=1000, price_per_hour__lte=3000)
        if value == "high":
            return queryset.filter(price_per_hour__gt=3000)
        return queryset


class EquipmentDetailInline(admin.StackedInline):
    model = EquipmentDetail
    extra = 0
    can_delete = True


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    # Список
    list_display = ("id", "title", "manufacturer", "price_per_hour", price_with_fee, "status", "time_create", brief_info, image_preview)
    list_display_links = ("id", "title")
    list_editable = ("status",)
    ordering = ("-time_create", "title")
    list_per_page = 10
    search_fields = ("title", "description", "manufacturer__name")
    list_filter = ("status", "manufacturer", PriceRangeFilter, "time_create", "tags")

    # Формы
    fields = ("title", "slug", "description", "manufacturer", "tags", "price_per_hour", "image", "status", "time_create", "time_update")
    readonly_fields = ("time_create", "time_update")
    prepopulated_fields = {"slug": ("title",)}

    inlines = [EquipmentDetailInline]

    # Действия
    @admin.action(description="Опубликовать выбранные")
    def set_published(self, request, queryset):
        updated = queryset.update(status=Equipment.Status.PUBLISHED)
        self.message_user(request, f"Опубликовано записей: {updated}", level=messages.SUCCESS)

    @admin.action(description="Снять с публикации")
    def set_draft(self, request, queryset):
        updated = queryset.update(status=Equipment.Status.DRAFT)
        self.message_user(request, f"Снято с публикации: {updated}", level=messages.WARNING)

    actions = ["set_published", "set_draft"]


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
