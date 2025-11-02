"""URLs para la aplicación certificates"""
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
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
from certificates.views.template_editor_views import (
    TemplateEditorView,
    TemplateEditorCreateView
)
# Import API views conditionally to handle missing dependencies
try:
    from certificates.api_views import (
        CertificateTemplateViewSet,
        TemplateElementViewSet,
        TemplateAssetViewSet,
        LaTeXValidationView,
        LaTeXRenderView,
    )
    API_VIEWS_AVAILABLE = True
except ImportError as e:
    # Create dummy views if dependencies are missing
    from rest_framework.viewsets import ViewSet
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import status
    
    class CertificateTemplateViewSet(ViewSet):
        def list(self, request):
            return Response({'error': 'WeasyPrint not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    class TemplateElementViewSet(ViewSet):
        def list(self, request):
            return Response({'error': 'WeasyPrint not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    class TemplateAssetViewSet(ViewSet):
        def list(self, request):
            return Response({'error': 'WeasyPrint not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    class LaTeXValidationView(APIView):
        def post(self, request):
            return Response({'error': 'WeasyPrint not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    class LaTeXRenderView(APIView):
        def post(self, request):
            return Response({'error': 'WeasyPrint not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    API_VIEWS_AVAILABLE = False

# Router para las APIs REST
router = DefaultRouter()
router.register(r'templates', CertificateTemplateViewSet, basename='template')
router.register(r'elements', TemplateElementViewSet, basename='element')
router.register(r'assets', TemplateAssetViewSet, basename='asset')

app_name = 'certificates'

urlpatterns = [
    # APIs REST para editor de plantillas
    path('api/', include(router.urls)),
    
    # APIs específicas para LaTeX
    path('api/latex/validate/', LaTeXValidationView.as_view(), name='latex-validate'),
    path('api/latex/render/', LaTeXRenderView.as_view(), name='latex-render'),
    
    # Página principal - redirige a consulta
    path('', RedirectView.as_view(pattern_name='certificates:query', permanent=False), name='home'),
    
    # Rutas de administración
    path('admin/import-excel/', ExcelImportView.as_view(), name='import_excel'),
    path('admin/import-external/', ExternalCertificateImportView.as_view(), name='import_external'),
    
    # Dashboard de estadísticas
    path('admin/dashboard/', dashboard_view, name='admin_dashboard'),
    path('admin/dashboard/refresh/', dashboard_refresh, name='dashboard_refresh'),
    
    # Editor de plantillas visual
    path('admin/template-editor/', TemplateEditorCreateView.as_view(), name='template_editor_create'),
    path('admin/template-editor/<int:template_id>/', TemplateEditorView.as_view(), name='template_editor'),
    
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
