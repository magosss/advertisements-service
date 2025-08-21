from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CityViewSet, CategoryViewSet, AdvertisementViewSet, 
    AdvertisementImageViewSet, FavoriteViewSet,
    AuthViewSet
)

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement')
router.register(r'images', AdvertisementImageViewSet, basename='image')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]
