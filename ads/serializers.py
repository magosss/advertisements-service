from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Advertisement, AdvertisementImage, Favorite


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории"""
    advertisements_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'advertisements_count', 'created_at']

    def get_advertisements_count(self, obj):
        return obj.advertisements.filter(status='active').count()


class AdvertisementImageSerializer(serializers.ModelSerializer):
    """Сериализатор для изображения объявления"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AdvertisementImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class AdvertisementListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка объявлений"""
    category = CategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'price', 'category', 'author', 'status',
            'location', 'is_featured', 'views_count', 'primary_image',
            'images_count', 'created_at', 'expires_at', 'is_expired'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return AdvertisementImageSerializer(primary_image, context=self.context).data
        return None

    def get_images_count(self, obj):
        return obj.images.count()


class AdvertisementDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра объявления"""
    category = CategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    images = AdvertisementImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'price', 'category', 'author',
            'status', 'location', 'contact_phone', 'contact_email',
            'is_featured', 'views_count', 'images', 'is_favorited',
            'created_at', 'updated_at', 'expires_at', 'is_expired'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объявления"""
    images = AdvertisementImageSerializer(many=True, required=False)

    class Meta:
        model = Advertisement
        fields = [
            'title', 'description', 'price', 'category', 'location',
            'contact_phone', 'contact_email', 'images'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['author'] = self.context['request'].user
        advertisement = Advertisement.objects.create(**validated_data)

        for image_data in images_data:
            AdvertisementImage.objects.create(advertisement=advertisement, **image_data)

        return advertisement

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        
        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем изображения
        if images_data:
            # Удаляем старые изображения
            instance.images.all().delete()
            # Создаем новые
            for image_data in images_data:
                AdvertisementImage.objects.create(advertisement=instance, **image_data)

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных объявлений"""
    advertisement = AdvertisementListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'advertisement', 'created_at']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания избранного"""
    class Meta:
        model = Favorite
        fields = ['advertisement']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_advertisement(self, value):
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, advertisement=value).exists():
            raise serializers.ValidationError("Объявление уже в избранном")
        return value
