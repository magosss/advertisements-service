from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from django.utils import timezone
from .models import City, Category, Advertisement, AdvertisementImage, Favorite
from .serializers import (
    CitySerializer, CategorySerializer, AdvertisementListSerializer, AdvertisementDetailSerializer,
    AdvertisementCreateSerializer, AdvertisementImageSerializer,
    FavoriteSerializer, FavoriteCreateSerializer
)
from .permissions import IsOwnerOrReadOnly


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для городов"""
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class AdvertisementViewSet(viewsets.ModelViewSet):
    """Представление для объявлений"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'city', 'status', 'author', 'is_featured']
    search_fields = ['title', 'description', 'location', 'city__name']
    ordering_fields = ['price', 'created_at', 'views_count', 'title']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Advertisement.objects.select_related('category', 'city', 'author').prefetch_related('images')
        
        # Фильтрация по статусу (по умолчанию показываем только активные)
        status_filter = self.request.query_params.get('status', 'active')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Фильтрация по цене
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Фильтрация по дате создания
        days = self.request.query_params.get('days')
        if days:
            try:
                days = int(days)
                queryset = queryset.filter(created_at__gte=timezone.now() - timezone.timedelta(days=days))
            except ValueError:
                pass
        
        # Фильтрация по местоположению
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return AdvertisementCreateSerializer
        elif self.action == 'retrieve':
            return AdvertisementDetailSerializer
        return AdvertisementListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Увеличивает счетчик просмотров"""
        advertisement = self.get_object()
        advertisement.views_count = F('views_count') + 1
        advertisement.save()
        advertisement.refresh_from_db()
        return Response({'views_count': advertisement.views_count})

    @action(detail=False, methods=['get'])
    def my_advertisements(self, request):
        """Получает объявления текущего пользователя"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Получает рекомендуемые объявления"""
        queryset = self.get_queryset().filter(is_featured=True, status='active')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Расширенный поиск объявлений"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'detail': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """Получает объявления по городу"""
        city_id = request.query_params.get('city_id')
        city_slug = request.query_params.get('city_slug')
        
        if not city_id and not city_slug:
            return Response({'detail': 'city_id or city_slug parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        elif city_slug:
            queryset = queryset.filter(city__slug=city_slug)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category_and_city(self, request):
        """Получает объявления по категории и городу"""
        category_id = request.query_params.get('category_id')
        category_slug = request.query_params.get('category_slug')
        city_id = request.query_params.get('city_id')
        city_slug = request.query_params.get('city_slug')
        
        if (not category_id and not category_slug) or (not city_id and not city_slug):
            return Response({
                'detail': 'Both category (id or slug) and city (id or slug) parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        # Фильтрация по категории
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        elif category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Фильтрация по городу
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        elif city_slug:
            queryset = queryset.filter(city__slug=city_slug)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdvertisementImageViewSet(viewsets.ModelViewSet):
    """Представление для изображений объявлений"""
    queryset = AdvertisementImage.objects.all()
    serializer_class = AdvertisementImageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return AdvertisementImage.objects.filter(advertisement__author=self.request.user)

    def perform_create(self, serializer):
        advertisement_id = self.request.data.get('advertisement')
        advertisement = Advertisement.objects.get(id=advertisement_id)
        if advertisement.author != self.request.user:
            raise PermissionError("You can only add images to your own advertisements")
        serializer.save()


class FavoriteViewSet(viewsets.ModelViewSet):
    """Представление для избранных объявлений"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('advertisement')

    def get_serializer_class(self):
        if self.action == 'create':
            return FavoriteCreateSerializer
        return FavoriteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def remove_from_favorites(self, request, pk=None):
        """Удаляет объявление из избранного"""
        favorite = self.get_object()
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def check_favorite(self, request):
        """Проверяет, находится ли объявление в избранном"""
        advertisement_id = request.query_params.get('advertisement_id')
        if not advertisement_id:
            return Response({'detail': 'advertisement_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_favorited = Favorite.objects.filter(
            user=request.user, 
            advertisement_id=advertisement_id
        ).exists()
        
        return Response({'is_favorited': is_favorited})
