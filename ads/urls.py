from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, AdvertisementViewSet, 
    AdvertisementImageViewSet, FavoriteViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement')
router.register(r'images', AdvertisementImageViewSet, basename='image')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]
