from django.urls import path

from . import views

urlpatterns = [
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/create/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<slug:equipment_slug>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('equipment/<slug:equipment_slug>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<slug:equipment_slug>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
    path('tags/', views.tags_list, name='tags_list'),
    path('analytics/', views.analytics_demo, name='analytics_demo'),
]
