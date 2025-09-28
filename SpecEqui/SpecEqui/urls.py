
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('equipment/', include('bid.urls')),
    path('users/', include('users.urls')),
]

# Customize Django admin titles for SpecEqui
admin.site.site_header = "Админ-панель"
admin.site.index_title = "Управление техникой и заявками"
admin.site.site_title = "Админка SpecEqui"