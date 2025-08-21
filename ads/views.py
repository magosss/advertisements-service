from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from .models import City, Category, Advertisement, AdvertisementImage, Favorite
from .serializers import (
    CitySerializer, CategorySerializer, AdvertisementListSerializer, AdvertisementDetailSerializer,
    AdvertisementCreateSerializer, AdvertisementImageSerializer,
    FavoriteSerializer, FavoriteCreateSerializer, CategoryWithUnviewedCountSerializer, 
    CategoryWithChildrenSerializer, UserSerializer
)
from .sms_service import SMSService
from .permissions import IsOwnerOrReadOnly


@method_decorator(csrf_exempt, name='dispatch')
class AuthViewSet(viewsets.ViewSet):
    """Представление для аутентификации"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Регистрация нового пользователя"""
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not all([username, email, password]):
            return Response({
                'error': 'Необходимо указать username, email и password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Пользователь с таким именем уже существует'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Пользователь с таким email уже существует'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Создаем токен для пользователя
            token, created = Token.objects.get_or_create(user=user)
            
            # Автоматически входим в систему
            login(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Пользователь успешно зарегистрирован'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Ошибка при создании пользователя: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Вход в систему"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([username, password]):
            return Response({
                'error': 'Необходимо указать username и password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Успешный вход в систему'
            })
        else:
            return Response({
                'error': 'Неверные учетные данные'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Выход из системы"""
        if request.user.is_authenticated:
            logout(request)
            return Response({
                'message': 'Успешный выход из системы'
            })
        else:
            return Response({
                'error': 'Пользователь не авторизован'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def send_sms_code(self, request):
        """Отправляет SMS код подтверждения"""
        phone = request.data.get('phone')
        
        if not phone:
            return Response({
                'error': 'Необходимо указать номер телефона'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Очищаем номер телефона
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        if not clean_phone.startswith('7') or len(clean_phone) != 11:
            return Response({
                'error': 'Неверный формат номера телефона'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sms_service = SMSService()
            result = sms_service.send_verification_code(clean_phone)
            
            if 'error' in result:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'message': 'Код отправлен',
                'phone': clean_phone
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Ошибка отправки SMS: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def verify_sms_code(self, request):
        """Проверяет SMS код и создает/авторизует пользователя"""
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        if not all([phone, code]):
            return Response({
                'error': 'Необходимо указать номер телефона и код'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Очищаем номер телефона
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        try:
            sms_service = SMSService()
            verify_result = sms_service.verify_code(clean_phone, code)
            
            if 'error' in verify_result:
                return Response({
                    'error': verify_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Ищем пользователя по номеру телефона
            try:
                user = User.objects.get(username=clean_phone)
                # Пользователь существует, авторизуем его
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data,
                    'message': 'Вход выполнен успешно',
                    'is_new_user': False
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                # Пользователь не существует, создаем нового
                user = User.objects.create_user(
                    username=clean_phone,
                    email=f"{clean_phone}@arbito.local",  # Временный email
                    password=User.objects.make_random_password(),  # Случайный пароль
                    first_name='',
                    last_name=''
                )
                
                # Сохраняем код у нового пользователя
                from .models import UserLastCode
                UserLastCode.update_or_create_code(user, clean_phone, code)
                
                # Авторизуем нового пользователя
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data,
                    'message': 'Пользователь создан и авторизован',
                    'is_new_user': True
                }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Ошибка верификации: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    
    @action(detail=False, methods=['get'])
    def user_info(self, request):
        """Получение информации о текущем пользователе"""
        if request.user.is_authenticated:
            return Response({
                'user': UserSerializer(request.user).data,
                'is_authenticated': True
            })
        else:
            return Response({
                'is_authenticated': False
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        """Удаление аккаунта пользователя"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Пользователь не авторизован'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Удаляем связанные данные пользователя
            from .models import UserLastCode, SMSVerification, Favorite
            from django.contrib.auth.models import User
            
            user = request.user
            
            # Удаляем SMS коды пользователя
            UserLastCode.objects.filter(user=user).delete()
            
            # Удаляем SMS верификации пользователя
            SMSVerification.objects.filter(phone=user.username).delete()
            
            # Удаляем избранное пользователя
            Favorite.objects.filter(user=user).delete()
            
            # Удаляем объявления пользователя (с изображениями)
            from .models import Advertisement, AdvertisementImage
            user_advertisements = Advertisement.objects.filter(author=user)
            for ad in user_advertisements:
                AdvertisementImage.objects.filter(advertisement=ad).delete()
            user_advertisements.delete()
            
            # Удаляем токены пользователя
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user=user).delete()
            
            # Удаляем самого пользователя
            user.delete()
            
            return Response({
                'message': 'Аккаунт успешно удален'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Ошибка удаления аккаунта: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    """Представление для категорий с количеством непросмотренных"""
    queryset = Category.objects.all()
    serializer_class = CategoryWithUnviewedCountSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Возвращает категории с фильтрацией по городам"""
        queryset = Category.objects.all()
        
        # Фильтр по уровню
        level = self.request.query_params.get('level')
        if level == '0':
            # Только родительские категории
            queryset = queryset.filter(parent__isnull=True)
        elif level == '1':
            # Только подкатегории
            queryset = queryset.filter(parent__isnull=False)
        
        # Фильтр по родительской категории
        parent_slug = self.request.query_params.get('parent')
        if parent_slug:
            queryset = queryset.filter(parent__slug=parent_slug)
        
        # Фильтр по городу
        city_id = self.request.query_params.get('city_id')
        if city_id:
            if city_id == 'all':
                # Показываем все категории (включая те, что доступны везде)
                pass
            else:
                try:
                    # Фильтруем по конкретному городу
                    # Показываем категории, которые либо доступны в этом городе,
                    # либо доступны везде (не имеют привязки к городам)
                    queryset = queryset.filter(
                        Q(cities__id=city_id) | Q(cities__isnull=True)
                    ).distinct()
                except ValueError:
                    pass
        
        return queryset

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия"""
        if self.action == 'retrieve' and self.request.query_params.get('with_children') == 'true':
            return CategoryWithChildrenSerializer
        return CategoryWithUnviewedCountSerializer

    @action(detail=True, methods=['get'])
    def children(self, request, slug=None):
        """Получает подкатегории конкретной категории"""
        category = self.get_object()
        children = category.children.all()
        serializer = CategoryWithUnviewedCountSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tree(self, request, slug=None):
        """Получает полное дерево категории с подкатегориями"""
        category = self.get_object()
        serializer = CategoryWithChildrenSerializer(category, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Получает полную иерархию всех категорий"""
        # Получаем только родительские категории
        parent_categories = Category.objects.filter(parent__isnull=True)
        serializer = CategoryWithChildrenSerializer(parent_categories, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def parents_only(self, request):
        """Получает только родительские категории"""
        parent_categories = Category.objects.filter(parent__isnull=True)
        serializer = CategoryWithUnviewedCountSerializer(parent_categories, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def subcategories_only(self, request):
        """Получает только подкатегории"""
        subcategories = Category.objects.filter(parent__isnull=False)
        serializer = CategoryWithUnviewedCountSerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """Получает категории, доступные в указанном городе"""
        city_id = request.query_params.get('city_id')
        
        if not city_id:
            return Response(
                {'error': 'city_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if city_id == 'all':
            # Показываем все категории
            queryset = Category.objects.filter(parent__isnull=True)
        else:
            try:
                # Фильтруем по конкретному городу
                queryset = Category.objects.filter(
                    parent__isnull=True
                ).filter(
                    Q(cities__id=city_id) | Q(cities__isnull=True)
                ).distinct()
            except ValueError:
                return Response(
                    {'error': 'Invalid city_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = CategoryWithUnviewedCountSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class AdvertisementViewSet(viewsets.ModelViewSet):
    """Представление для объявлений"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'city', 'status', 'author', 'is_featured']
    search_fields = ['title', 'description', 'location', 'city__name']
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Advertisement.objects.select_related('category', 'city', 'author').prefetch_related('images')
        
        # Фильтрация по статусу (по умолчанию показываем только активные)
        status_filter = self.request.query_params.get('status', 'active')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Фильтрация по городу
        city_id = self.request.query_params.get('city_id')
        if city_id:
            if city_id == 'all':
                # Показываем все объявления
                pass
            else:
                try:
                    # Фильтруем по конкретному городу
                    queryset = queryset.filter(city_id=city_id)
                except ValueError:
                    pass
        
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

    def create(self, request, *args, **kwargs):
        """Переопределяем create для поддержки файлов"""
        # Получаем файлы из request.FILES
        files = request.FILES.getlist('images')
        
        # Создаем копию данных без файлов
        data = {}
        for key, value in request.data.items():
            if key != 'images':
                data[key] = value
        
        # Добавляем файлы в данные
        if files:
            data['images'] = files
        
        # Создаем сериализатор с обновленными данными
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



    @action(detail=False, methods=['get'])
    def my_advertisements(self, request):
        """Получает объявления текущего пользователя"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Для my_advertisements возвращаем только активные объявления
        queryset = Advertisement.objects.select_related('category', 'city', 'author').prefetch_related('images')
        queryset = queryset.filter(author=request.user, status='active')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Получает объявления текущего пользователя на модерации"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Для pending используем базовый queryset без фильтрации по статусу
        queryset = Advertisement.objects.select_related('category', 'city', 'author').prefetch_related('images')
        queryset = queryset.filter(author=request.user, status='pending')
        
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

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Увеличивает счетчик просмотров объявления"""
        advertisement = self.get_object()
        advertisement.increment_views()
        return Response({
            'status': 'success',
            'views_count': advertisement.views_count
        })


@method_decorator(csrf_exempt, name='dispatch')
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


@method_decorator(csrf_exempt, name='dispatch')
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







