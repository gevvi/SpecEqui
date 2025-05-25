from django.urls import path

from . import views

urlpatterns = [
    # Главная страница.
    path('', views.homepage),
    path('submit-order/', views.submit_order, name='submit_order'),
]
