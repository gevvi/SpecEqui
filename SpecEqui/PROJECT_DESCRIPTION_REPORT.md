# Описание приложения и деталей его реализации (SpecEqui)

В этом отчёте описаны ключевые части проекта SpecEqui: проектирование базы данных, маршрутизация, представления, шаблоны, а также профиль пользователя, управление паролями и права доступа. Формат отчёта соответствует примеру, но отражает именно текущий проект.

## 1. Проектирование базы данных

Задача: определить, какие сущности понадобятся и как они связаны.

Основная модель Equipment. В файле `bid/models.py` описан класс `Equipment`, в котором хранится основная информация о единицах спецтехники:

```python
class Equipment(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Название техники")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за час, ₽")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    status = models.IntegerField(choices=Status.choices, default=Status.DRAFT, verbose_name="Публикация")
    image = models.ImageField(upload_to='equipment_images/', blank=True, null=True, verbose_name="Изображение техники")

    # Владелец записи (создатель оборудования)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_equipment',
        verbose_name='Владелец'
    )

    # Лайки (многие-ко-многим) — пользователи, которым понравилось оборудование
    # добавлено динамически через Equipment.add_to_class('likes', ManyToManyField(...))

    # Справочники: Производитель (FK) и Теги (M2M)
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.SET_NULL, related_name='equipment', verbose_name="Производитель", null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='equipment', verbose_name="Теги", blank=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-time_create']
        indexes = [models.Index(fields=['-time_create'])]
        verbose_name = 'Единица техники'
        verbose_name_plural = 'Единицы техники'
        permissions = [
            ('can_publish_equipment', 'Может публиковать оборудование'),
            ('can_manage_equipment', 'Может управлять оборудованием'),
            ('can_view_equipment_analytics', 'Может просматривать аналитику оборудования'),
        ]
```

- `title` и `description` — базовая информация о технике.
- `status` определяет публикацию (черновик/опубликовано).
- `price_per_hour` — стоимость аренды в час.
- `image` — загрузка изображения техники.
- `time_create`/`time_update` — аудит создания/изменения.
- Дополнительные права (permissions) позволяют гибко управлять доступом к публикации и аналитике.
- Поле `owner` фиксирует автора записи (для проверок прав).
- Связи: один-ко-многим с `Manufacturer`, многие-ко-многим с `Tag`.

Справочники: Manufacturer и Tag

```python
class Manufacturer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Производитель")
    country = models.CharField(max_length=100, verbose_name="Страна")

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тег")
```

Подробное описание классов моделей

- Manufacturer
  - Назначение: справочник производителей техники (бренд, страна происхождения).
  - Компоненты:
    - Поля: `name` (название бренда), `country` (страна-производитель).
    - Связи: обратная связь `equipment` (related_name) из `Equipment` — позволяет получить все единицы техники данного производителя.
  - Поведение: обычно используется в выпадающих списках форм для классификации оборудования и в аналитике (агрегации по производителям).

- Tag
  - Назначение: тематические теги для классификации техники (например, «манипулятор», «экскаватор»).
  - Компоненты:
    - Поля: `name` — уникальное, обеспечивает нормализованный справочник.
    - Связи: M2M с `Equipment` через `equipment` (related_name) — техника может иметь несколько тегов.
  - Поведение: используется в фильтрации/каталогизации, а также в аналитике (подсчёт количества техники по тегам).

Модель Comment

Для обратной связи пользователей предусмотрена модель комментариев к технике:

```python
class Comment(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='comments', verbose_name='Оборудование')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_comments', verbose_name='Автор')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
```

- `equipment` связывает комментарий с конкретной единицей техники.
- `author` — пользователь, оставивший комментарий.
- `text` — содержимое комментария.
- `created_at` — автоматическое время создания.

Подробное описание класса Comment
- Назначение: хранит пользовательские отзывы/заметки к технике.
- Компоненты:
  - Поля: `text` (содержимое), `created_at` (когда оставлен), внешние ключи на `Equipment` и `User`.
  - Связи: `equipment.comments` — доступ к списку комментариев техники; `author.equipment_comments` — все комментарии пользователя.
- Поведение: удаляется каскадно при удалении связанной техники или автора, упорядочен по дате создания (сначала новые в интерфейсе).

Лайки к технике (в одно нажатие)

```python
# Добавлено динамически:
Equipment.add_to_class(
    'likes',
    models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_equipment', blank=True, verbose_name='Лайки')
)
```

- Пользователь может лайкнуть/снять лайк единицу техники.
- Счётчик лайков — это `equipment.likes.count()`.

Рисунок 1 – Структура базы данных (Equipment — Manufacturer, Tag, Comment; M2M лайки).

---

## 2. Маршрутизация

Задача: связать URL-адреса с представлениями приложения.

Корневой `urls.py`

```python
# SpecEqui/SpecEqui/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('equipment/', include('bid.urls')),
    path('users/', include('users.urls')),
]
```

Маршруты приложения `bid`

```python
# SpecEqui/bid/urls.py
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
```

Маршруты приложения `users`

```python
# SpecEqui/users/urls.py
app_name = 'users'
urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
```

Статические пути (например, `add-equipment-custom/`, `upload/`) расположены отдельно от детальных с `<slug:equipment_slug>/` для предотвращения конфликтов. Порядок в `bid/urls.py` подобран так, чтобы Django корректно сопоставлял URL.

---

## 3. Представления и шаблоны

Задача: реализовать логику обработки запросов и отрисовку данных.

Общий миксин

```python
# SpecEqui/bid/utils.py (DataMixin)
class DataMixin(ContextMixin):
    title = None
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        # добавление title, меню и др. вспомогательных данных
        return context

Подробное описание класса DataMixin
- Назначение: единая точка расширения контекста шаблонов (заголовки страниц, общее меню, параметры пагинации и служебные значения).
- Компоненты: атрибут `title` (может устанавливаться во вьюхах), метод `get_context_data` дополняет контекст.
- Поведение: наследуется всеми основными представлениями для единообразия UI и снижения дублирования.
```

Список (EquipmentListView)

```python
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
        ...  # фильтрация и сортировка
        return queryset

Подробное описание класса EquipmentListView
- Назначение: каталог опубликованной техники с поиском, сортировкой и пагинацией.
- Компоненты:
  - Источник данных: `Equipment.published` (кастомный менеджер, фильтрующий по статусу «Опубликовано»).
  - Запрос: дополнительные фильтры по `q` (поиск по названию) и `sort` (цена/дата). Предзагрузки `select_related('manufacturer')` и `prefetch_related('tags')` сокращают число SQL-запросов.
  - Пагинация: `paginate_by = 5`.
- Поведение: формирует итоговый QuerySet в зависимости от параметров запроса; возвращает его в шаблон `bid/equipment_list.html`.
```

Детальная страница + комментарии + лайки (EquipmentDetailView)

```python
class EquipmentDetailView(DataMixin, DetailView):
    model = Equipment
    template_name = 'bid/equipment_detail.html'
    context_object_name = 'equipment'
    slug_url_kwarg = 'equipment_slug'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['equipment'].title
        context['comment_form'] = CommentForm()
        context['likes_count'] = context['equipment'].likes.count()
        user = self.request.user
        context['has_liked'] = user.is_authenticated and context['equipment'].likes.filter(id=user.id).exists()
        return context

Подробное описание класса EquipmentDetailView
- Назначение: отображение карточки техники с подробностями, списком комментариев и текущим состоянием лайка пользователя.
- Компоненты:
  - Идентификация объекта: `slug_url_kwarg = 'equipment_slug'` — поиск по человеку-понятному URL.
  - Контекст: `comment_form` (форма отправки новых комментариев), `likes_count` (счётчик лайков), `has_liked` (флаг — поставил ли лайк текущий пользователь).
- Поведение: рендерит шаблон `bid/equipment_detail.html`; сам не обрабатывает POST — для этого есть отдельные вьюхи.
```

Создание/редактирование/удаление (с проверками прав)

```python
class EquipmentCreateView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = EquipmentModelForm
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class EquipmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, DataMixin, UpdateView):
    def test_func(self):
        equipment = self.get_object()
        return equipment.owner_id == self.request.user.id or self.request.user.is_staff

class EquipmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DataMixin, DeleteView):
    def test_func(self):
        equipment = self.get_object()
        return equipment.owner_id == self.request.user.id or self.request.user.is_staff

Подробное описание классов EquipmentCreate/Update/DeleteView
- EquipmentCreateView
  - Назначение: создание записи техники через `ModelForm`.
  - Поведение: в `form_valid` автоматически назначает владельца `owner = request.user`; после успешного сохранения — редирект по стандартной логике `CreateView`.
- EquipmentUpdateView
  - Назначение: редактирование существующей записи.
  - Компоненты: `UserPassesTestMixin` с `test_func` — владелец или `staff`.
  - Поведение: при отсутствии прав возвращает 403; шаблон редактирования тот же, что и для создания.
- EquipmentDeleteView
  - Назначение: удаление записи техники.
  - Компоненты: такой же `test_func` для проверки прав.
  - Поведение: после удаления — редирект на список (через `success_url`).
```

Добавление комментариев и лайки (в одно нажатие)

```python
class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, equipment_slug):
        equipment = get_object_or_404(Equipment, slug=equipment_slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(equipment=equipment, author=request.user, text=form.cleaned_data['text'])
        return redirect('equipment_detail', equipment_slug=equipment.slug)

class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, equipment_slug):
        equipment = get_object_or_404(Equipment, slug=equipment_slug)
        user = request.user
        liked = False
        if equipment.likes.filter(id=user.id).exists():
            equipment.likes.remove(user)
        else:
            equipment.likes.add(user)
            liked = True
        return JsonResponse({'liked': liked, 'likesCount': equipment.likes.count()})

Подробное описание классов AddCommentView и ToggleLikeView
- AddCommentView
  - Назначение: приём и валидация формы комментария (POST).
  - Компоненты: `LoginRequiredMixin` (для защиты от анонимного спама), `CommentForm` (валидирует текст).
  - Поведение: привязывает новый комментарий к конкретной технике и текущему пользователю; после сохранения — редирект на детальную страницу.
- ToggleLikeView
  - Назначение: переключение лайка техники в одно нажатие (AJAX).
  - Компоненты: `JsonResponse` как результат; доступ только авторизованным (через миксин).
  - Поведение: если лайк уже стоит — снимает, иначе добавляет; возвращает текущее состояние и новый счётчик.
```

Формы

```python
# SpecEqui/bid/forms.py
class EquipmentModelForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['title','slug','description','price_per_hour','manufacturer','tags','status','image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

Подробное описание форм
- EquipmentModelForm
  - Назначение: редактирование полей модели `Equipment` в удобном для пользователя виде.
  - Компоненты: набор полей, виджеты (например, многострочный `Textarea` для `description`).
  - Поведение: отдаётся в шаблоны создания/редактирования; валидация — на уровне формы и модели.
- CommentForm
  - Назначение: компактный ввод текста комментария.
  - Поведение: минимальный набор полей — связь с объектом и автором ставится на уровне вьюхи, чтобы нельзя было подменить отношения через форму.
```

Шаблон `equipment_detail.html` (фрагмент: права, комментарии, лайки)

```html
{% if user.is_authenticated and user.is_staff %}
  <a href="{% url 'equipment_update' equipment_slug=equipment.slug %}">Редактировать</a> |
  <a href="{% url 'equipment_delete' equipment_slug=equipment.slug %}">Удалить</a> |
{% elif user.is_authenticated and equipment.owner_id == user.id %}
  <a href="{% url 'equipment_update' equipment_slug=equipment.slug %}">Редактировать</a> |
  <a href="{% url 'equipment_delete' equipment_slug=equipment.slug %}">Удалить</a> |
{% endif %}

<h3>Комментарии</h3>
<div>
  {% for c in equipment.comments.all %}
    <div>
      <strong>{{ c.author.username }}</strong>
      <span class="text-muted" style="font-size:12px;">{{ c.created_at|date:"d.m.Y H:i" }}</span>
      <div>{{ c.text|linebreaks }}</div>
    </div>
  {% empty %}
    <p>Пока нет комментариев.</p>
  {% endfor %}
</div>

{% if user.is_authenticated %}
  <form method="post" action="{% url 'equipment_add_comment' equipment_slug=equipment.slug %}">
    {% csrf_token %}
    {{ comment_form.as_p }}
    <button type="submit" class="btn btn-primary">Отправить</button>
  </form>
{% endif %}

<button id="likeBtn" class="btn btn-outline-primary btn-sm">
  ❤ <span id="likesCount">{{ likes_count }}</span>
  </button>

Подробности шаблона
- Блоки прав: кнопки редактирования/удаления видны только сотрудникам (`is_staff`) и владельцу записи.
- Комментарии: лента с именем автора, временем и содержимым; форма отправки доступна только авторизованным.
- Лайки: кнопка запускает AJAX-запрос к `ToggleLikeView`; счётчик обновляется без перезагрузки страницы.
```

Рисунок 2 – Комментарии и кнопка лайка на детальной странице.

---

## 4. Профиль пользователя и управление паролем

Задача: реализовать профиль, смену и сброс пароля по e-mail, а также регистрацию.

Профиль

```python
class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users:login')
    template_name = 'users/profile.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user'] = self.request.user
        return ctx
```

Регистрация

```python
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('equipment_list')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

Подробное описание пользовательских разделов
- ProfileView
  - Назначение: персональная страница пользователя (данные об аккаунте, навигация к операциям смены/сброса пароля).
  - Компоненты: защита `LoginRequiredMixin`, шаблон `users/profile.html`, где доступны `{{ user.username }}`, `{{ user.email }}`.
- Регистрация (`register`)
  - Назначение: упрощённая регистрация с автоматическим входом.
  - Компоненты: стандартная форма `UserCreationForm` с проверкой паролей.
  - Поведение: при успешной регистрации — `login()` и редирект на список техники.
- Смена/сброс пароля
  - Назначение: безопасные операции управления паролем.
  - Компоненты: `PasswordChangeView`, `PasswordResetView` и связанные классы; SMTP-настройки для отправки писем.
  - Поведение: стандартные сценарии Django — форма запроса письма, письмо со ссылкой, установка нового пароля, подтверждающие экраны.

Смена пароля (конкретная реализация)

```python
# SpecEqui/users/views.py
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Форма смены пароля.
    """
    login_url = reverse_lazy('users:login')
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')
```

- Шаблон `users/password_change_form.html` содержит поля `old_password`, `new_password1`, `new_password2` и стандартную валидацию Django.

Восстановление пароля (конкретная реализация)

```python
# SpecEqui/users/views.py
class CustomPasswordResetView(PasswordResetView):
    """
    Шаг 1: форма запроса сброса пароля (ввод e-mail, отправка письма).
    """
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
```

SMTP-настройки (Yandex)

```python
# SpecEqui/SpecEqui/settings.py
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'danielalyohin@yandex.ru'
EMAIL_HOST_PASSWORD = 'rvpibhbuiptjkpph'
DEFAULT_FROM_EMAIL = 'SpecEqui <danielalyohin@yandex.ru>'
```

Комментарии по работе механизма
- Пользователь заполняет e-mail в форме `password_reset_form.html`. Сервис отправляет письмо со ссылкой.
- Переход по ссылке открывает `password_reset_confirm.html`, где задаётся новый пароль.
- После успешной смены отображается `password_reset_complete.html`. Все шаги используют встроенные проверки токенов и срок действия ссылки (`PASSWORD_RESET_TIMEOUT`).
```

Смена пароля / Сброс пароля

Используются стандартные классы `PasswordChangeView`, `PasswordResetView` и др., с кастомными шаблонами. SMTP-настройки указаны в `settings.py` (Yandex SMTP). После запроса сброса приходит письмо со ссылкой на восстановление.

Рисунок 3 – Профиль пользователя. Рисунок 4 – Смена/восстановление пароля.

---

## 5. Админ-панель и разрешения

Задача: предоставить администраторам удобные инструменты и гибкие права.

- В `Equipment.Meta.permissions` добавлены пользовательские права (например, `can_publish_equipment`). Их можно выдавать конкретным группам.
- В админке можно управлять записями (списки, поиск, фильтры по тегам/производителю и т.д. — при необходимости расширяется через `ModelAdmin`).
- Пример назначения прав группам и пользователям аналогичен приведённому в вашем шаблоне отчёта (используются стандартные модели Django `Group`, `Permission`).

Рисунок 5 – Списки в админ-панели, фильтрация и массовые действия (при необходимости добавляются).

---

### Настройка админки EquipmentAdmin

```python
# SpecEqui/bid/admin.py
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    # Список
    list_display = (
        "id", "title", "manufacturer", "price_per_hour", price_with_fee,
        "status", "time_create", brief_info, image_preview
    )
    list_display_links = ("id", "title")
    list_editable = ("status",)
    ordering = ("-time_create", "title")
    list_per_page = 10
    search_fields = ("title", "description", "manufacturer__name")
    list_filter = ("status", "manufacturer", PriceRangeFilter, "time_create", "tags")

    # Формы
    fields = (
        "title", "slug", "description", "manufacturer", "tags",
        "price_per_hour", "image", "status", "time_create", "time_update"
    )
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
```

Описание кода
- list_filter: настроено на `("status", "manufacturer", PriceRangeFilter, "time_create", "tags")`. Свойство определяет фильтры в боковой панели админки для модели `Equipment`.
  - `status` — фильтрация по статусу публикации.
  - `manufacturer` — фильтрация по связанному производителю.
  - `PriceRangeFilter` — пользовательский фильтр диапазонов цены/час (см. класс ниже).
  - `time_create` — фильтр по дате создания.
  - `tags` — фильтр по тегам (M2M).
- Горизонтальный фильтр для `tags`: поскольку `tags` — поле Many-to-Many, Django Admin предоставляет удобный виджет выбора нескольких значений (горизонтальный список) даже без явного `filter_horizontal = ['tags']`. Это упрощает добавление и удаление тегов для каждого объекта.
- `prepopulated_fields = {"slug": ("title",)}` — автоподстановка слага из названия при вводе.
- `readonly_fields` — системные поля времени доступны только для чтения.
- `list_display` — в списке добавлены вычисляемые колонки `price_with_fee` (цена с сервисным коэффициентом), `brief_info` (краткое описание), `image_preview` (мини-превью изображения).
- `actions` — массовые операции публикации/снятия с публикации для выделенных записей.
- `inlines = [EquipmentDetailInline]` — на странице редактирования `Equipment` показывается связанный блок `EquipmentDetail` (характеристики двигателя/трансмиссии и пр.).

Пользовательский фильтр цены

```python
class PriceRangeFilter(SimpleListFilter):
    title = "Диапазон цены/час"
    parameter_name = "price_range"
    def lookups(self, request, model_admin):
        return [("low", "До 1 000 ₽"), ("mid", "1 000–3 000 ₽"), ("high", "Более 3 000 ₽")]
    def queryset(self, request, queryset):
        value = self.value()
        if value == "low":
            return queryset.filter(price_per_hour__lt=1000)
        if value == "mid":
            return queryset.filter(price_per_hour__gte=1000, price_per_hour__lte=3000)
        if value == "high":
            return queryset.filter(price_per_hour__gt=3000)
        return queryset
```

Вспомогательные отображения

```python
@admin.display(description="Краткое описание")
def brief_info(obj):
    # усечённое описание

@admin.display(description="Цена с сервисом (₽)")
def price_with_fee(obj):
    # расчёт цены с коэффициентом 1.15

@admin.display(description='Превью изображения')
def image_preview(obj):
    # мини-картинка из поля image
```

Итог: админка предоставляет удобные списки с поиском, фильтрами (в т.ч. пользовательскими), массовыми действиями и инлайнами, ускоряя повседневную модерацию и наполнение данных.

---

## Заключение

В SpecEqui реализованы:

- Модели для техники, производителей, тегов и комментариев; лайки «в одно нажатие» для техники.
- Формы и вьюхи для создания/редактирования/удаления записей с проверкой прав: редактировать и удалять может только владелец или `staff`.
- Комментарии и лайки без перезагрузки страницы (AJAX для лайков), что повышает интерактивность.
- Полный цикл управления учётной записью: регистрация, профиль, смена и восстановление пароля.
- Гибкая маршрутизация, удобные шаблоны и общий миксин контекста.

Архитектура оставляет код модульным и расширяемым: добавление новых разделов и сущностей выполняется с минимальным дублированием.


