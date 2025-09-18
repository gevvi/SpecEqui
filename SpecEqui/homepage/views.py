from django.shortcuts import render,redirect
from django.contrib import messages
from bid.models import Equipment

menu = ["O нас", "Автопарк", "Обратная связь",]
items = None

def homepage(request):
    equipment = Equipment.published.all()
    data = {'title': 'Главная страница',
            'items': {e.title: int(e.price_per_hour) for e in equipment}}
    return render(request, 'homepage/homepage.html', data)


def submit_order(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        messages.success(
            request, f'Спасибо за заказ {product_name}! Мы свяжемся с вами в ближайшее время.')
        return redirect('homepage')

    return redirect('homepage')
