"""URLs para la aplicación certificates"""
from django.urls import path
from certificates.views.admin_views import ExcelImportView
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
    # Rutas de administración
    path('admin/import-excel/', ExcelImportView.as_view(), name='import_excel'),
    path('admin/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/dashboard/charts/', DashboardChartsAPIView.as_view(), name='dashboard_charts'),
    path('admin/dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard_stats'),
    
    # Rutas públicas
    path('consulta/', CertificateQueryView.as_view(), name='query'),
    path('certificado/<uuid:uuid>/descargar/', CertificateDownloadView.as_view(), name='download'),
    path('verificar/<uuid:uuid>/', CertificateVerificationView.as_view(), name='verify'),
]
