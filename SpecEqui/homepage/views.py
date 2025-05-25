from django.shortcuts import render,redirect
from django.contrib import messages

menu = ["O нас", "Автопарк", "Обратная связь",]
items = {"Автокран" : 3000, 
         "Манипулятор": 2800, 
         "Экскаватор": 2500, 
         "Автовышка": 2500}

def homepage(request):
    data = {'title': 'Главная страница',
            'items': items}
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
