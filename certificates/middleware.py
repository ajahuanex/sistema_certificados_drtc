"""Middleware personalizado para la aplicación certificates"""
from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited


class RatelimitMiddleware:
    """Middleware para manejar excepciones de rate limiting"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """Maneja excepciones de rate limiting"""
        if isinstance(exception, Ratelimited):
            return render(
                request,
                'certificates/rate_limit_exceeded.html',
                {
                    'message': 'Ha excedido el límite de solicitudes permitidas. Por favor, intente nuevamente en unos minutos.'
                },
                status=429
            )
        return None
