from django import forms
from .models import Equipment, Comment


# 1. Собственный валидатор: проверка заглавной буквы в начале названия
def validate_title_capitalized(value):
    if value and not value[0].isupper():
        raise forms.ValidationError(
            'Название техники должно начинаться с заглавной буквы',
            code='not_capitalized'
        )


# 3. Собственный валидатор: проверка разумной цены за час
def validate_reasonable_price(value):
    if value < 100:
        raise forms.ValidationError(
            'Цена за час аренды не может быть меньше 100 рублей',
            code='too_cheap'
        )
    if value > 50000:
        raise forms.ValidationError(
            'Цена за час аренды не может быть больше 50 000 рублей',
            code='too_expensive'
        )


# Несвязанная с моделью форма для добавления техники
class EquipmentForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        label='Название спецтехники',
        validators=[validate_title_capitalized],
        help_text='До 255 символов, должно начинаться с заглавной буквы'
    )
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='Описание техники',
        help_text='Дополнительная информация о технике (необязательно)'
    )
    price_per_hour = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Цена за час аренды, ₽',
        validators=[validate_reasonable_price],
        help_text='Цена от 100 до 50 000 рублей с двумя знаками после точки'
    )
    image = forms.ImageField(
        required=False,
        label='Изображение техники',
        help_text='JPG/PNG до 5 МБ (необязательно)'
    )


# Форма, связанная с моделью Equipment
class EquipmentModelForm(forms.ModelForm):
    # Переопределяем title, чтобы применить валидатор
    title = forms.CharField(
        max_length=255,
        label='Название спецтехники',
        validators=[validate_title_capitalized],
        help_text='Должно начинаться с заглавной буквы'
    )
    
    # Переопределяем price_per_hour для добавления валидатора
    price_per_hour = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Цена за час аренды, ₽',
        validators=[validate_reasonable_price],
        help_text='Цена от 100 до 50 000 рублей'
    )

    class Meta:
        model = Equipment
        fields = [
            'title',
            'slug',
            'description',
            'price_per_hour',
            'manufacturer',
            'tags',
            'status',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'status': forms.Select(choices=Equipment.Status.choices),
        }



class UploadForm(forms.Form):
    file = forms.FileField(
        label='Выберите файл',
        help_text='Максимум 10 МБ. Любой тип файла.'
    )

    def clean_file(self):
        f = self.cleaned_data['file']
        if f.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Файл слишком большой (больше 10 МБ)')
        return f


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Оставьте комментарий...'})
        }
