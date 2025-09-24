from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F, Value, Count, Avg, Sum, DecimalField, ExpressionWrapper
from django.db.models.functions import Concat
from .models import Equipment, Tag, Manufacturer
from decimal import Decimal


class EquipmentListView(ListView):
    model = Equipment
    template_name = 'bid/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Equipment.published.select_related('manufacturer').prefetch_related('tags').all()
        q = self.request.GET.get('q')
        sort = self.request.GET.get('sort')
        if q:
            queryset = queryset.filter(title__icontains=q)
        if sort in {'price', '-price', 'new', 'old'}:
            if sort == 'price':
                queryset = queryset.order_by('price_per_hour')
            elif sort == '-price':
                queryset = queryset.order_by('-price_per_hour')
            elif sort == 'new':
                queryset = queryset.order_by('-time_create')
            elif sort == 'old':
                queryset = queryset.order_by('time_create')
        return queryset


class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'bid/equipment_detail.html'
    context_object_name = 'equipment'
    slug_url_kwarg = 'equipment_slug'


class EquipmentCreateView(CreateView):
    model = Equipment
    fields = ['title', 'slug', 'description', 'price_per_hour', 'status', 'manufacturer', 'tags']
    template_name = 'bid/equipment_form.html'


class EquipmentUpdateView(UpdateView):
    model = Equipment
    fields = ['title', 'slug', 'description', 'price_per_hour', 'status', 'manufacturer', 'tags']
    template_name = 'bid/equipment_form.html'
    slug_url_kwarg = 'equipment_slug'


class EquipmentDeleteView(DeleteView):
    model = Equipment
    template_name = 'bid/equipment_confirm_delete.html'
    success_url = reverse_lazy('equipment_list')
    slug_url_kwarg = 'equipment_slug'


def bidwindow(request, pk):
    return redirect('equipment_list')

def tags_list(request):
    tags = Tag.objects.annotate(num_equipment=Count('equipment')).order_by('name')
    return render(request, 'bid/tags_list.html', {
        'title': 'Теги',
        'tags': tags,
    })


def analytics_demo(request):
    # Q: составные условия (пример: дороже 2500 или название содержит "Экскаватор")
    q_equipment = Equipment.objects.filter(
        Q(price_per_hour__gt=2500) | Q(title__icontains='экскават')
    )

    # F/Value: вычисляемые поля и константы
    equipment_with_tax = Equipment.objects.annotate(
        price_with_tax=ExpressionWrapper(
            F('price_per_hour') * Value(Decimal('1.20')),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        status_message=Value('Отличная спецтехника'),
    ).values('title', 'price_per_hour', 'price_with_tax', 'status_message')[:20]

    # Агрегаты
    totals = Equipment.objects.aggregate(
        total_count=Count('id'),
        avg_price=Avg('price_per_hour'),
        sum_price=Sum('price_per_hour'),
    )

    # Группировка по производителю
    by_manufacturer = (
        Manufacturer.objects
        .annotate(equipment_count=Count('equipment'))
        .values('name', 'country', 'equipment_count')
        .order_by('-equipment_count', 'name')
    )

    # Группировка по тегам
    by_tag = (
        Tag.objects
        .annotate(equipment_count=Count('equipment'))
        .values('name', 'equipment_count')
        .order_by('-equipment_count', 'name')
    )

    context = {
        'q_equipment': q_equipment[:20],
        'equipment_with_tax': list(equipment_with_tax),
        'totals': totals,
        'by_manufacturer': list(by_manufacturer),
        'by_tag': list(by_tag),
    }
    return render(request, 'bid/analytics.html', context)
