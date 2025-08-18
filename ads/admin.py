from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Advertisement, AdvertisementImage, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'advertisements_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    def advertisements_count(self, obj):
        return obj.advertisements.filter(status='active').count()
    advertisements_count.short_description = 'Количество объявлений'


class AdvertisementImageInline(admin.TabularInline):
    model = AdvertisementImage
    extra = 1
    fields = ['image', 'caption', 'is_primary']


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'price', 'status', 
        'is_featured', 'views_count', 'created_at', 'is_expired_display'
    ]
    list_filter = [
        'status', 'category', 'is_featured', 'created_at', 
        'expires_at', 'author'
    ]
    search_fields = ['title', 'description', 'author__username', 'location']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'is_expired']
    inlines = [AdvertisementImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'price', 'category', 'author')
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


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
