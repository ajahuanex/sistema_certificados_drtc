"""Personalización del sitio de administración"""
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse


class CertificatesAdminSite(AdminSite):
    """Sitio de administración personalizado para certificados"""
    
    site_header = "Sistema de Certificados DRTC Puno"
    site_title = "Certificados DRTC"
    index_title = "Administración de Certificados"
    
    def index(self, request, extra_context=None):
        """Página principal del admin con enlace al dashboard"""
        extra_context = extra_context or {}
        
        # Agregar enlace al dashboard
        extra_context['dashboard_url'] = reverse('certificates:dashboard')
        
        return super().index(request, extra_context)


# Instancia personalizada del admin
admin_site = CertificatesAdminSite(name='certificates_admin')