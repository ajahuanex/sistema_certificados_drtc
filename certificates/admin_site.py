from django.contrib import admin
from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    """Admin site personalizado con CSS mejorado"""
    
    site_header = "DRTC Puno - Administración de Certificados"
    site_title = "DRTC Puno Admin"
    index_title = "Panel de Administración"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# Instancia del admin site personalizado
admin_site = CustomAdminSite(name='admin')
