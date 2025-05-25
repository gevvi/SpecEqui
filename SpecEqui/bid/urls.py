from django.urls import path

from . import views

urlpatterns = [
    # Главная страница.
    path('<pk>', views.bidwindow),
]
