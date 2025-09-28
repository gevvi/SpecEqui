from django.views.generic.base import ContextMixin

MENU = [
    {'title': 'Главная', 'url_name': 'equipment_list'},
    {'title': 'О сайте', 'url_name': 'homepage:homepage'},
    {'title': 'Добавить (Form)', 'url_name': 'add_equipment_custom'},
    {'title': 'Добавить (ModelForm)', 'url_name': 'add_equipment_model'},
    {'title': 'Загрузка файла', 'url_name': 'upload_file'},
    {'title': 'Теги', 'url_name': 'tags_list'},
    {'title': 'Аналитика', 'url_name': 'analytics_demo'},
]

class DataMixin(ContextMixin):
    """
    Добавляет в контекст:
      - global menu
      - title, если задано
      - page_range для ListView с пагинацией
    """
    title = None

    def get_context_data(self, *, object_list=None, **kwargs):
        # Убеждаемся, что object_list инициализирован
        if object_list is None and hasattr(self, 'get_queryset'):
            object_list = self.get_queryset()
        
        # Сначала получаем весь контекст от родительских классов,
        # в том числе paginator, page_obj, object_list
        context = super().get_context_data(object_list=object_list, **kwargs)

        # Базовый контекст
        context['menu'] = MENU
        if self.title:
            context['title'] = self.title

        # Если есть пагинация — вычисляем ограниченный диапазон страниц
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        if paginator and page_obj:
            total = paginator.num_pages
            current = page_obj.number
            window = 2
            start = max(current - window, 1)
            end   = min(current + window, total)
            context['page_range'] = range(start, end + 1)

        return context
