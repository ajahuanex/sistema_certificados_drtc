"""URLs para la aplicación certificates"""
from django.urls import path
from django.views.generic import RedirectView
from certificates.views.admin_views import (
    ExcelImportView,
    ExternalCertificateImportView,
    DownloadParticipantsTemplateView,
    DownloadExternalCertificatesTemplateView,
    PDFImportView,
    QRProcessingView,
    ExportForSigningView,
    FinalImportView,
    ProcessingStatusView,
)
from certificates.views.public_views import (
    CertificateQueryView,
    CertificateDownloadView,
    CertificateVerificationView,
    CertificatePreviewView,
)
from certificates.views.dashboard_views import (
    dashboard_view,
    dashboard_refresh
)

app_name = 'certificates'

urlpatterns = [
    # Página principal - redirige a consulta
    path('', RedirectView.as_view(pattern_name='certificates:query', permanent=False), name='home'),
    
    # Rutas de administración
    path('admin/import-excel/', ExcelImportView.as_view(), name='import_excel'),
    path('admin/import-external/', ExternalCertificateImportView.as_view(), name='import_external'),
    
    # Dashboard de estadísticas
    path('admin/dashboard/', dashboard_view, name='admin_dashboard'),
    path('admin/dashboard/refresh/', dashboard_refresh, name='dashboard_refresh'),
    
    # Descargar plantillas Excel
    path('admin/download-template/participants/', DownloadParticipantsTemplateView.as_view(), name='download_participants_template'),
    path('admin/download-template/external/', DownloadExternalCertificatesTemplateView.as_view(), name='download_external_template'),
    
    # Procesamiento de certificados con QR
    path('admin/pdf-import/', PDFImportView.as_view(), name='pdf_import'),
    path('admin/qr-processing/', QRProcessingView.as_view(), name='qr_processing'),
    path('admin/export-signing/', ExportForSigningView.as_view(), name='export_signing'),
    path('admin/final-import/', FinalImportView.as_view(), name='final_import'),
    path('admin/processing-status/', ProcessingStatusView.as_view(), name='processing_status'),
    
    # Rutas públicas
    path('consulta/', CertificateQueryView.as_view(), name='query'),
    path('certificado/<uuid:uuid>/descargar/', CertificateDownloadView.as_view(), name='download'),
    path('verificar/<uuid:uuid>/', CertificateVerificationView.as_view(), name='verify'),
    
    # Preview público de certificados con QR
    path('certificado/<uuid:certificate_uuid>/preview/', CertificatePreviewView.as_view(), name='certificate_preview'),
]
