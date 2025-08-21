from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Отключаем CSRF для всех API запросов
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
