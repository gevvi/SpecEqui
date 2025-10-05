from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import EmailOrUsernameAuthenticationForm as AuthenticationForm



def login_user(request):
    """
    Логин по e-mail или username.
    """
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url or 'equipment_list')
    else:
        form = AuthenticationForm(request)
    return render(request, 'users/login.html', {'form': form, 'next': next_url})


def logout_user(request):
    """
    Выход и редирект на главную.
    """
    logout(request)
    return redirect('equipment_list')


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Страница профиля текущего пользователя.
    """
    login_url = reverse_lazy('users:login')
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Форма смены пароля.
    """
    login_url = reverse_lazy('users:login')
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """
    Страница подтверждения смены пароля.
    """
    login_url = reverse_lazy('users:login')
    template_name = 'users/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    """
    Шаг 1: форма запроса сброса пароля (ввод e-mail, отправка письма).
    """
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Шаг 2: страница, показываемая после отправки письма.
    """
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Шаг 3: форма установки нового пароля (переход по ссылке из письма).
    """
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Шаг 4: страница, показываемая после успешного сброса пароля.
    """
    template_name = 'users/password_reset_complete.html'


def register(request):
    """
    Регистрация нового пользователя.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('equipment_list')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
