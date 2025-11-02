"""
URLs para las APIs REST del editor de plantillas.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CertificateTemplateViewSet,
    TemplateElementViewSet,
    TemplateAssetViewSet,
)

# Crear router y registrar viewsets
router = DefaultRouter()
router.register(r'templates', CertificateTemplateViewSet, basename='template')
router.register(r'elements', TemplateElementViewSet, basename='element')
router.register(r'assets', TemplateAssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]
