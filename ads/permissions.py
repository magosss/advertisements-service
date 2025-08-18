from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцу объекта редактировать его.
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех запросов
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем запись только владельцу
        return obj.author == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцу или администратору редактировать объект.
    """
    
    def has_object_permission(self, request, view, obj):
        # Администраторы могут все
        if request.user.is_staff:
            return True
        
        # Владелец может редактировать
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
