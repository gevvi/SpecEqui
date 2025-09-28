from django.core.management.base import BaseCommand
from bid.models import Equipment, Tag, Manufacturer, EquipmentDetail


class Command(BaseCommand):
    help = 'Очищает базу данных от тестовых данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтвердить удаление всех данных',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'Для удаления всех данных используйте флаг --confirm'
                )
            )
            return

        # Удаляем все данные
        equipment_count = Equipment.objects.count()
        tag_count = Tag.objects.count()
        manufacturer_count = Manufacturer.objects.count()
        detail_count = EquipmentDetail.objects.count()

        EquipmentDetail.objects.all().delete()
        Equipment.objects.all().delete()
        Tag.objects.all().delete()
        Manufacturer.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Удалено: {equipment_count} единиц оборудования, '
                f'{tag_count} тегов, {manufacturer_count} производителей, '
                f'{detail_count} деталей оборудования'
            )
        )
