"""
Context processors para la aplicación certificates.
Agregan variables globales a todos los templates.
"""
from django.urls import reverse


def dashboard_context(request):
    """
    Agrega la URL del dashboard a todos los templates del admin.
    Solo disponible para usuarios staff.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'dashboard_url': reverse('certificates:admin_dashboard')
        }
    return {}
