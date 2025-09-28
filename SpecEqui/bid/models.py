from django.db import models
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Equipment.Status.PUBLISHED)


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
    
    # Relations
    # One-to-many: Производитель -> Единицы техники
    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.SET_NULL,
        related_name='equipment',
        verbose_name="Производитель",
        null=True,
        blank=True,
    )

    # Many-to-many: Теги <-> Единицы техники
    tags = models.ManyToManyField(
        'Tag',
        related_name='equipment',
        verbose_name="Теги",
        blank=True,
    )

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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('equipment_detail', kwargs={'equipment_slug': self.slug})


class Manufacturer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Производитель")
    country = models.CharField(max_length=100, verbose_name="Страна")

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        ordering = ['name']
        permissions = [
            ('can_manage_manufacturers', 'Может управлять производителями'),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тег")

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
        permissions = [
            ('can_manage_tags', 'Может управлять тегами'),
        ]

    def __str__(self):
        return self.name


class EquipmentDetail(models.Model):
    # One-to-one: Доп. сведения об единице техники
    equipment = models.OneToOneField(
        Equipment,
        on_delete=models.CASCADE,
        related_name='detail',
        verbose_name="Единица техники",
    )
    engine = models.CharField(max_length=100, verbose_name="Двигатель")
    transmission = models.CharField(max_length=100, verbose_name="Коробка передач")
    mileage = models.PositiveIntegerField(verbose_name="Пробег, км", null=True, blank=True)

    class Meta:
        verbose_name = 'Характеристики техники'
        verbose_name_plural = 'Характеристики техники'

    def __str__(self):
        return f"Детали {self.equipment.title}"
