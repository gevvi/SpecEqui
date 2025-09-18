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

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-time_create']
        indexes = [models.Index(fields=['-time_create'])]
        verbose_name = 'Единица техники'
        verbose_name_plural = 'Единицы техники'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('equipment_detail', kwargs={'equipment_slug': self.slug})
