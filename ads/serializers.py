from rest_framework import serializers
from django.contrib.auth.models import User
from .models import City, Category, Advertisement, AdvertisementImage, Favorite


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class CitySerializer(serializers.ModelSerializer):
    """Сериализатор для города"""
    advertisements_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'is_active', 'advertisements_count', 'created_at']

    def get_advertisements_count(self, obj):
        return obj.advertisements.filter(status='active').count()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории"""
    advertisements_count = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    cities = CitySerializer(many=True, read_only=True)
    available_cities_display = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'advertisements_count', 'children_count', 'level', 'cities', 'available_cities_display', 'created_at']

    def get_available_cities_display(self, obj):
        return obj.get_available_cities_display()

    def get_advertisements_count(self, obj):
        return obj.advertisements.filter(status='active').count()

    def get_children_count(self, obj):
        return obj.children.count()


class CategoryWithChildrenSerializer(CategorySerializer):
    """Сериализатор для категории с подкатегориями"""
    children = CategorySerializer(many=True, read_only=True)
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['children']


class CategoryWithUnviewedCountSerializer(CategorySerializer):
    """Сериализатор категории с количеством непросмотренных объявлений"""
    unviewed_count = serializers.SerializerMethodField()
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['unviewed_count']
    
    def get_unviewed_count(self, obj):
        try:
            user = self.context['request'].user
            if user.is_authenticated:
                # Получаем city_id из query параметров запроса
                request = self.context['request']
                city_id = request.query_params.get('city_id')
                return obj.get_unviewed_count_for_user(user, city_id)
            return 0
        except Exception as e:
            print(f"Ошибка в get_unviewed_count: {e}")
            return 0


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
    city = CitySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'price', 'category', 'city', 'author', 'status',
            'location', 'is_featured', 'primary_image',
            'images_count', 'views_count', 'created_at', 'expires_at', 'is_expired'
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
    city = CitySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    images = AdvertisementImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'price', 'category', 'city', 'author',
            'status', 'location', 'contact_phone', 'contact_email',
            'is_featured', 'images', 'is_favorited', 'views_count',
            'created_at', 'updated_at', 'expires_at', 'is_expired'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объявления"""
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'price', 'category', 'city',
            'status', 'location', 'is_featured', 'images', 'images_count', 'views_count', 'created_at', 'expires_at', 'is_expired', 'author'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'expires_at', 'is_expired', 'views_count']

    def get_expires_at(self, obj):
        """Вычисляем дату истечения объявления (30 дней после создания)"""
        if obj.created_at:
            from datetime import timedelta
            return obj.created_at + timedelta(days=30)
        return None

    def get_is_expired(self, obj):
        """Проверяем, истекло ли объявление"""
        if obj.created_at:
            from datetime import timedelta
            expires_at = obj.created_at + timedelta(days=30)
            return timezone.now() > expires_at
        return False

    def get_images_count(self, obj):
        return obj.images.count()

    def to_representation(self, instance):
        """Переопределяем представление для добавления полных объектов"""
        data = super().to_representation(instance)
        
        # Добавляем expires_at
        if instance.created_at:
            from datetime import timedelta
            expires_at = instance.created_at + timedelta(days=30)
            data['expires_at'] = expires_at.isoformat()
        
        # Добавляем полный объект author
        if instance.author:
            data['author'] = {
                'id': instance.author.id,
                'username': instance.author.username,
                'first_name': instance.author.first_name or '',
                'last_name': instance.author.last_name or '',
                'email': instance.author.email or ''
            }
        
        # Добавляем полный объект category
        if instance.category:
            data['category'] = {
                'id': instance.category.id,
                'name': instance.category.name,
                'slug': instance.category.slug,
                'description': instance.category.description or '',
                'icon': instance.category.icon or '',
                'parent': instance.category.parent.id if instance.category.parent else None,
                'advertisements_count': instance.category.advertisements.filter(status='active').count(),
                'children_count': instance.category.children.count(),
                'level': instance.category.level,
                'cities': [],
                'available_cities_display': instance.category.get_available_cities_display(),
                'created_at': instance.category.created_at.isoformat() if instance.category.created_at else None
            }
        
        # Добавляем полный объект city
        if instance.city:
            data['city'] = {
                'id': instance.city.id,
                'name': instance.city.name,
                'slug': instance.city.slug,
                'is_active': instance.city.is_active,
                'advertisements_count': instance.city.advertisements.filter(status='active').count(),
                'created_at': instance.city.created_at.isoformat() if instance.city.created_at else None
            }
        
        # Добавляем изображения
        images = []
        primary_image = None
        
        for image in instance.images.all():
            image_data = {
                'id': image.id,
                'image': self.context['request'].build_absolute_uri(image.image.url) if image.image else None,
                'image_url': self.context['request'].build_absolute_uri(image.image.url) if image.image else None,
                'caption': image.caption or '',
                'is_primary': image.is_primary,
                'created_at': image.created_at.isoformat() if image.created_at else None
            }
            images.append(image_data)
            
            # Если это первое изображение или помечено как основное, используем его как primary_image
            if primary_image is None or image.is_primary:
                primary_image = image_data
        
        data['images'] = images
        data['primary_image'] = primary_image
        
        return data

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['author'] = self.context['request'].user
        advertisement = Advertisement.objects.create(**validated_data)

        # Создаем записи для изображений
        for index, image_file in enumerate(images_data):
            # Первое изображение автоматически становится главным
            is_primary = index == 0
            AdvertisementImage.objects.create(
                advertisement=advertisement,
                image=image_file,
                is_primary=is_primary
            )

        # Возвращаем объект с полными данными для iOS приложения
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
            for index, image_file in enumerate(images_data):
                # Первое изображение автоматически становится главным
                is_primary = index == 0
                AdvertisementImage.objects.create(
                    advertisement=instance,
                    image=image_file,
                    is_primary=is_primary
                )

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



