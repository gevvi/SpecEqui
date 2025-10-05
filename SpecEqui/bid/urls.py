from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/create/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<slug:equipment_slug>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<slug:equipment_slug>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
    path('equipment/<slug:equipment_slug>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('equipment/<slug:equipment_slug>/comment/', views.AddCommentView.as_view(), name='equipment_add_comment'),
    path('equipment/<slug:equipment_slug>/like/', views.ToggleLikeView.as_view(), name='equipment_toggle_like'),
    path('tags/', views.TagsListView.as_view(), name='tags_list'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics_demo'),
    
    path('add-equipment-custom/', views.AddEquipmentCustomView.as_view(), name='add_equipment_custom'),
    path('add-equipment-model/', views.EquipmentCreateView.as_view(), name='add_equipment_model'),
    path('upload/', views.UploadFileView.as_view(), name='upload_file'),
]

# Подключение медиа-файлов для разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
