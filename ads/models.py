from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Модель категории объявлений"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Иконка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    """Модель объявления"""
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('inactive', 'Неактивно'),
        ('pending', 'На модерации'),
        ('rejected', 'Отклонено'),
    ]

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена',
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='advertisements',
        verbose_name='Категория'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='advertisements',
        verbose_name='Автор'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Статус'
    )
    location = models.CharField(max_length=200, blank=True, verbose_name='Местоположение')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    contact_email = models.EmailField(blank=True, verbose_name='Email')
    
    # Дополнительные поля
    is_featured = models.BooleanField(default=False, verbose_name='Рекомендуемое')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    expires_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='Дата истечения'
    )

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем дату истечения через 30 дней
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Проверяет, истекло ли объявление"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class AdvertisementImage(models.Model):
    """Модель изображения объявления"""
    advertisement = models.ForeignKey(
        Advertisement, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Объявление'
    )
    image = models.ImageField(
        upload_to='advertisements/%Y/%m/%d/', 
        verbose_name='Изображение'
    )
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')
    is_primary = models.BooleanField(default=False, verbose_name='Главное изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Изображение объявления'
        verbose_name_plural = 'Изображения объявлений'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Изображение для {self.advertisement.title}"

    def save(self, *args, **kwargs):
        # Если это главное изображение, убираем флаг у других изображений
        if self.is_primary:
            AdvertisementImage.objects.filter(
                advertisement=self.advertisement,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Favorite(models.Model):
    """Модель избранных объявлений"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites',
        verbose_name='Пользователь'
    )
    advertisement = models.ForeignKey(
        Advertisement, 
        on_delete=models.CASCADE, 
        related_name='favorited_by',
        verbose_name='Объявление'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'advertisement']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.advertisement.title}"
