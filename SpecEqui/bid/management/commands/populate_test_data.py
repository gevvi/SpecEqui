from django.core.management.base import BaseCommand
from django.utils.text import slugify
from bid.models import Equipment, Tag, Manufacturer, EquipmentDetail
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для демонстрации пагинации'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=25,
            help='Количество записей оборудования для создания (по умолчанию: 25)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Создаем производителей
        manufacturers_data = [
            {'name': 'Caterpillar', 'country': 'США'},
            {'name': 'Komatsu', 'country': 'Япония'},
            {'name': 'Volvo', 'country': 'Швеция'},
            {'name': 'JCB', 'country': 'Великобритания'},
            {'name': 'Liebherr', 'country': 'Германия'},
            {'name': 'Hyundai', 'country': 'Южная Корея'},
            {'name': 'Hitachi', 'country': 'Япония'},
            {'name': 'Doosan', 'country': 'Южная Корея'},
        ]
        
        manufacturers = []
        for data in manufacturers_data:
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=data['name'],
                defaults={'country': data['country']}
            )
            manufacturers.append(manufacturer)
            if created:
                self.stdout.write(f'Создан производитель: {manufacturer.name}')

        # Создаем теги
        tags_data = [
            'Экскаватор', 'Бульдозер', 'Погрузчик', 'Кран', 'Самосвал',
            'Бетономешалка', 'Асфальтоукладчик', 'Манипулятор', 'Грейдер',
            'Трактор', 'Фронтальный погрузчик', 'Мини-экскаватор',
            'Сваебойная машина', 'Каток', 'Буровая установка'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            if created:
                self.stdout.write(f'Создан тег: {tag.name}')

        # Создаем оборудование
        equipment_types = [
            'Экскаватор', 'Бульдозер', 'Фронтальный погрузчик', 'Кран',
            'Самосвал', 'Бетономешалка', 'Асфальтоукладчик', 'Манипулятор',
            'Грейдер', 'Трактор', 'Мини-экскаватор', 'Сваебойная машина',
            'Каток', 'Буровая установка', 'Подъемник'
        ]

        for i in range(1, count + 1):
            equipment_type = random.choice(equipment_types)
            manufacturer = random.choice(manufacturers)
            
            # Генерируем уникальный slug
            base_slug = slugify(f"{equipment_type} {manufacturer.name} {i}")
            slug = base_slug
            counter = 1
            while Equipment.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Создаем оборудование
            equipment = Equipment.objects.create(
                title=f"{equipment_type} {manufacturer.name} {i}",
                slug=slug,
                description=f"Высококачественный {equipment_type.lower()} от производителя {manufacturer.name}. "
                           f"Идеально подходит для строительных работ. "
                           f"Год выпуска: {random.randint(2015, 2024)}. "
                           f"Состояние: отличное.",
                price_per_hour=Decimal(str(random.randint(1000, 10000))),
                manufacturer=manufacturer,
                status=Equipment.Status.PUBLISHED
            )

            # Добавляем случайные теги
            equipment_tags = random.sample(tags, random.randint(1, 3))
            equipment.tags.set(equipment_tags)

            # Создаем детали оборудования (с вероятностью 70%)
            if random.random() < 0.7:
                engines = ['Дизельный', 'Газовый', 'Электрический', 'Гибридный']
                transmissions = ['Автоматическая', 'Механическая', 'Вариатор']
                
                EquipmentDetail.objects.create(
                    equipment=equipment,
                    engine=random.choice(engines),
                    transmission=random.choice(transmissions),
                    mileage=random.randint(1000, 50000)
                )

            self.stdout.write(f'Создано оборудование: {equipment.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано {count} единиц оборудования с тестовыми данными!'
            )
        )
