from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Equipment


class EquipmentListView(ListView):
    model = Equipment
    template_name = 'bid/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Equipment.published.all()
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
    fields = ['title', 'slug', 'description', 'price_per_hour', 'status']
    template_name = 'bid/equipment_form.html'


class EquipmentUpdateView(UpdateView):
    model = Equipment
    fields = ['title', 'slug', 'description', 'price_per_hour', 'status']
    template_name = 'bid/equipment_form.html'
    slug_url_kwarg = 'equipment_slug'


class EquipmentDeleteView(DeleteView):
    model = Equipment
    template_name = 'bid/equipment_confirm_delete.html'
    success_url = reverse_lazy('equipment_list')
    slug_url_kwarg = 'equipment_slug'


def bidwindow(request, pk):
    return redirect('equipment_list')

# Create your views here.
