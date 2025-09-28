import os
import uuid
import re

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView, FormView
)
from django.urls import reverse_lazy
from django.db.models import Q, F, Value, Count, Avg, Sum, DecimalField, ExpressionWrapper
from django.db.models.functions import Concat
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Equipment, Tag, Manufacturer
from .forms import EquipmentForm, EquipmentModelForm, UploadForm
from .utils import DataMixin
from decimal import Decimal


def generate_slug(title):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    slug = title.lower()
    for cyr, lat in translit_dict.items():
        slug = slug.replace(cyr, lat)

    slug = re.sub(r'[^a-z0-9\-]', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')

    if not slug:
        slug = 'equipment'
    
    return slug


class EquipmentListView(DataMixin, ListView):
    model = Equipment
    template_name = 'bid/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 5
    title = 'Специальное оборудование'

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


class EquipmentDetailView(DataMixin, DetailView):
    model = Equipment
    template_name = 'bid/equipment_detail.html'
    context_object_name = 'equipment'
    slug_url_kwarg = 'equipment_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['equipment'].title
        return context


class EquipmentCreateView(DataMixin, CreateView):
    model = Equipment
    form_class = EquipmentModelForm
    template_name = 'bid/add_equipment_model.html'
    success_url = reverse_lazy('equipment_list')
    title = 'Добавить оборудование (ModelForm)'


class EquipmentUpdateView(DataMixin, UpdateView):
    model = Equipment
    form_class = EquipmentModelForm
    template_name = 'bid/add_equipment_model.html'
    success_url = reverse_lazy('equipment_list')
    slug_url_kwarg = 'equipment_slug'
    title = 'Редактировать оборудование'


class EquipmentDeleteView(DataMixin, DeleteView):
    model = Equipment
    template_name = 'bid/equipment_confirm_delete.html'
    success_url = reverse_lazy('equipment_list')
    slug_url_kwarg = 'equipment_slug'
    title = 'Удалить оборудование'


class TagsListView(DataMixin, ListView):
    model = Tag
    template_name = 'bid/tags_list.html'
    context_object_name = 'tags'
    title = 'Теги'

    def get_queryset(self):
        return Tag.objects.annotate(num_equipment=Count('equipment')).order_by('name')


class AnalyticsView(DataMixin, TemplateView):
    template_name = 'bid/analytics.html'
    title = 'Аналитика'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        q_equipment = Equipment.objects.filter(
            Q(price_per_hour__gt=2500) | Q(title__icontains='экскават')
        )

        equipment_with_tax = Equipment.objects.annotate(
            price_with_tax=ExpressionWrapper(
                F('price_per_hour') * Value(Decimal('1.20')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            status_message=Value('Отличная спецтехника'),
        ).values('title', 'price_per_hour', 'price_with_tax', 'status_message')[:20]


        totals = Equipment.objects.aggregate(
            total_count=Count('id'),
            avg_price=Avg('price_per_hour'),
            sum_price=Sum('price_per_hour'),
        )

        by_manufacturer = (
            Manufacturer.objects
            .annotate(equipment_count=Count('equipment'))
            .values('name', 'country', 'equipment_count')
            .order_by('-equipment_count', 'name')
        )

        by_tag = (
            Tag.objects
            .annotate(equipment_count=Count('equipment'))
            .values('name', 'equipment_count')
            .order_by('-equipment_count', 'name')
        )

        context.update({
            'q_equipment': q_equipment[:20],
            'equipment_with_tax': list(equipment_with_tax),
            'totals': totals,
            'by_manufacturer': list(by_manufacturer),
            'by_tag': list(by_tag),
        })
        return context


class AddEquipmentCustomView(DataMixin, FormView):
    form_class = EquipmentForm
    template_name = 'bid/add_equipment_custom.html'
    success_url = reverse_lazy('equipment_list')
    title = 'Добавить оборудование (Form)'

    def form_valid(self, form):
        cd = form.cleaned_data
        base_slug = generate_slug(cd['title'])
        slug = base_slug
        counter = 1
        while Equipment.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        equipment = Equipment.objects.create(
            title=cd['title'],
            slug=slug,
            description=cd['description'],
            price_per_hour=cd['price_per_hour'],
            status=Equipment.Status.DRAFT
        )
        
        image = cd.get('image')
        if image:
            equipment.image = image
            equipment.save()
        return super().form_valid(form)


class UploadFileView(DataMixin, FormView):
    form_class = UploadForm
    template_name = 'bid/upload.html'
    success_url = reverse_lazy('upload_file')
    title = 'Загрузка файла'

    def form_valid(self, form):
        f = form.cleaned_data['file']
        ext = os.path.splitext(f.name)[1]
        new_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join('uploads', new_name)
        saved_path = default_storage.save(path, f)
        self.request.session['uploaded_file_link'] = settings.MEDIA_URL + saved_path
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['link'] = self.request.session.get('uploaded_file_link')
        return context
