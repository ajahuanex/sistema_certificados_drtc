"""URLs para la aplicación certificates"""
from django.urls import path
from django.views.generic import RedirectView
from certificates.views.admin_views import (
    ExcelImportView,
    ExternalCertificateImportView,
    DownloadParticipantsTemplateView,
    DownloadExternalCertificatesTemplateView
)
from certificates.views.public_views import (
    CertificateQueryView,
    CertificateDownloadView,
    CertificateVerificationView,
)
from certificates.views.dashboard_views import (
    DashboardView,
    DashboardChartsAPIView,
    DashboardStatsAPIView
)

app_name = 'certificates'

urlpatterns = [
    # Página principal - redirige a consulta
    path('', RedirectView.as_view(pattern_name='certificates:query', permanent=False), name='home'),
    
    # Rutas de administración
    path('admin/import-excel/', ExcelImportView.as_view(), name='import_excel'),
    path('admin/import-external/', ExternalCertificateImportView.as_view(), name='import_external'),
    path('admin/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/dashboard/charts/', DashboardChartsAPIView.as_view(), name='dashboard_charts'),
    path('admin/dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard_stats'),
    
    # Descargar plantillas Excel
    path('admin/download-template/participants/', DownloadParticipantsTemplateView.as_view(), name='download_participants_template'),
    path('admin/download-template/external/', DownloadExternalCertificatesTemplateView.as_view(), name='download_external_template'),
    
    # Rutas públicas
    path('consulta/', CertificateQueryView.as_view(), name='query'),
    path('certificado/<uuid:uuid>/descargar/', CertificateDownloadView.as_view(), name='download'),
    path('verificar/<uuid:uuid>/', CertificateVerificationView.as_view(), name='verify'),
]
