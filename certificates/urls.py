"""URLs para la aplicación certificates"""
from django.urls import path
from certificates.views.admin_views import ExcelImportView
from certificates.views.public_views import (
    CertificateQueryView,
    CertificateDownloadView,
    CertificateVerificationView,
)

app_name = 'certificates'

urlpatterns = [
    # Ruta de importación Excel (admin)
    path('admin/import-excel/', ExcelImportView.as_view(), name='import_excel'),
    
    # Rutas públicas
    path('consulta/', CertificateQueryView.as_view(), name='query'),
    path('certificado/<uuid:uuid>/descargar/', CertificateDownloadView.as_view(), name='download'),
    path('verificar/<uuid:uuid>/', CertificateVerificationView.as_view(), name='verify'),
]
