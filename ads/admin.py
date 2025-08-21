from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import City, Category, Advertisement, AdvertisementImage, Favorite, SMSVerification, UserLastCode


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'advertisements_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def advertisements_count(self, obj):
        return obj.advertisements.filter(status='active').count()
    advertisements_count.short_description = 'Количество объявлений'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'advertisements_count', 'children_count', 'level', 'available_cities', 'created_at']
    list_filter = ['parent', 'cities', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'level']
    filter_horizontal = ['cities']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'icon', 'parent')
        }),
        ('Города', {
            'fields': ('cities',),
            'description': 'Оставьте пустым, чтобы категория была доступна во всех городах'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def advertisements_count(self, obj):
        return obj.advertisements.filter(status='active').count()
    advertisements_count.short_description = 'Количество объявлений'

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Подкатегории'

    def level(self, obj):
        return obj.level
    level.short_description = 'Уровень'

    def available_cities(self, obj):
        return obj.get_available_cities_display()
    available_cities.short_description = 'Доступные города'


class AdvertisementImageInline(admin.TabularInline):
    model = AdvertisementImage
    extra = 1
    fields = ['image', 'caption', 'is_primary']


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'city', 'price', 'status', 
        'is_featured', 'views_count_display', 'created_at', 'is_expired_display'
    ]
    list_filter = [
        'status', 'category', 'city', 'is_featured', 'created_at', 
        'expires_at', 'author'
    ]
    search_fields = ['title', 'description', 'author__username', 'location', 'city__name']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'is_expired']
    inlines = [AdvertisementImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'price', 'category', 'city', 'author')
        }),
        ('Статус и настройки', {
            'fields': ('status', 'is_featured', 'views_count')
        }),
        ('Контактная информация', {
            'fields': ('location', 'contact_phone', 'contact_email')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'expires_at', 'is_expired')
        }),
    )

    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Истекло</span>')
        return format_html('<span style="color: green;">Активно</span>')
    is_expired_display.short_description = 'Статус истечения'

    def views_count_display(self, obj):
        return format_html('<span style="color: blue; font-weight: bold;">{}</span>', obj.views_count)
    views_count_display.short_description = 'Просмотры'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category', 'city')


@admin.register(AdvertisementImage)
class AdvertisementImageAdmin(admin.ModelAdmin):
    list_display = ['advertisement', 'image_preview', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['advertisement__title', 'caption']
    readonly_fields = ['created_at']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Предварительный просмотр'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'advertisement', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'advertisement__title']
    readonly_fields = ['created_at']



    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'advertisement')


@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone', 'code', 'is_verified', 'is_expired', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['phone']
    readonly_fields = ['created_at', 'expires_at', 'is_expired']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Истек'


@admin.register(UserLastCode)
class UserLastCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'code', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'phone']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# Расширяем админку пользователей для отображения SMS кодов
class UserLastCodeInline(admin.TabularInline):
    model = UserLastCode
    extra = 0
    readonly_fields = ['phone', 'code', 'created_at']
    can_delete = False
    max_num = 1
    
    def has_add_permission(self, request, obj=None):
        return False


# Перерегистрируем UserAdmin с нашим inline
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [UserLastCodeInline]
