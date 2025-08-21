from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string


class City(models.Model):
    """Модель города"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории объявлений"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Иконка')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='Родительская категория'
    )
    cities = models.ManyToManyField(
        City,
        blank=True,
        verbose_name='Города',
        help_text='Оставьте пустым, чтобы категория была доступна во всех городах'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def get_unviewed_count_for_user(self, user, city_id=None):
        """Получает количество объявлений в категории (теперь просто возвращает общее количество)"""
        try:
            # Если это родительская категория, считаем сумму всех подкатегорий
            if self.is_parent:
                total_ads = 0
                for child in self.get_all_children():
                    total_ads += child.get_unviewed_count_for_user(user, city_id)
                return total_ads
            
            # Для дочерних категорий считаем только объявления в текущей категории
            from django.db.models import Q
            ads_filter = Q(category=self, status='active')

            # Добавляем фильтр по городу, если указан
            if city_id and city_id != 'all':
                ads_filter &= Q(city_id=city_id)

            return Advertisement.objects.filter(ads_filter).count()
        except Exception as e:
            print(f"Ошибка в get_unviewed_count_for_user: {e}")
            return 0

    @property
    def is_parent(self):
        """Проверяет, является ли категория родительской"""
        return self.children.exists()

    @property
    def is_child(self):
        """Проверяет, является ли категория дочерней"""
        return self.parent is not None

    @property
    def level(self):
        """Возвращает уровень вложенности категории"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def get_all_children(self):
        """Получает все дочерние категории (рекурсивно)"""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_all_parents(self):
        """Получает всех родителей категории"""
        parents = []
        parent = self.parent
        while parent:
            parents.append(parent)
            parent = parent.parent
        return parents

    def is_available_in_city(self, city):
        """Проверяет, доступна ли категория в указанном городе"""
        # Если города не указаны, категория доступна везде
        if not self.cities.exists():
            return True
        # Иначе проверяем, есть ли указанный город в списке
        return self.cities.filter(id=city.id).exists()

    def get_available_cities_display(self):
        """Возвращает строку с доступными городами для отображения"""
        if not self.cities.exists():
            return "Все города"
        city_names = [city.name for city in self.cities.all()]
        return ", ".join(city_names)


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
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='advertisements',
        verbose_name='Город',
        null=True,
        blank=True
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

    def increment_views(self):
        """Увеличивает счетчик просмотров объявления"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


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


class SMSVerification(models.Model):
    """Модель для SMS-верификации"""
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    code = models.CharField(max_length=6, verbose_name='Код подтверждения')
    is_verified = models.BooleanField(default=False, verbose_name='Подтвержден')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expires_at = models.DateTimeField(verbose_name='Дата истечения')
    
    class Meta:
        verbose_name = 'SMS-верификация'
        verbose_name_plural = 'SMS-верификации'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS для {self.phone}"
    
    def is_expired(self):
        """Проверяет, истек ли код"""
        return timezone.now() > self.expires_at
    
    def generate_code(self):
        """Генерирует новый код подтверждения"""
        self.code = ''.join(random.choices(string.digits, k=4))
        self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        self.save()
        return self.code


class UserLastCode(models.Model):
    """Модель для хранения последнего SMS кода пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='last_sms_code')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    code = models.CharField(max_length=4, verbose_name='Последний код')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Последний код пользователя'
        verbose_name_plural = 'Последние коды пользователей'
    
    def __str__(self):
        return f"Код {self.code} для {self.user.username}"
    
    @classmethod
    def update_or_create_code(cls, user, phone, code):
        """Обновляет или создает последний код для пользователя"""
        obj, created = cls.objects.update_or_create(
            user=user,
            defaults={
                'phone': phone,
                'code': code,
            }
        )
        return obj