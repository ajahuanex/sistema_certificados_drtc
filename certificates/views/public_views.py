"""Vistas públicas para consulta y verificación de certificados"""
from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404, render
from django.http import FileResponse, Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from certificates.models import Certificate, AuditLog
from certificates.forms import DNIQueryForm


def get_client_ip(request):
    """Obtiene la dirección IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def handler429(request, exception=None):
    """Manejador personalizado para errores 429 (Too Many Requests)"""
    return render(
        request,
        'certificates/rate_limit_exceeded.html',
        {
            'message': 'Ha excedido el límite de solicitudes permitidas. Por favor, intente nuevamente en unos minutos.'
        },
        status=429
    )


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class CertificateQueryView(TemplateView):
    """Vista pública para consultar certificados por DNI"""
    template_name = 'certificates/query.html'

    def get_context_data(self, **kwargs):
        """Agrega el formulario al contexto"""
        context = super().get_context_data(**kwargs)
        context['form'] = DNIQueryForm()
        return context

    def post(self, request, *args, **kwargs):
        """Procesa la búsqueda de certificados por DNI"""
        form = DNIQueryForm(request.POST)
        
        if form.is_valid():
            dni = form.cleaned_data['dni']
            
            # Buscar certificados por DNI con optimización de queries
            certificates = Certificate.objects.filter(
                participant__dni=dni
            ).select_related(
                'participant',
                'participant__event'
            ).order_by('-participant__event__event_date')
            
            # Convertir a lista para evitar queries adicionales
            certificates_list = list(certificates)
            
            # Registrar consulta en AuditLog
            AuditLog.objects.create(
                action_type='QUERY',
                user=request.user if request.user.is_authenticated else None,
                description=f'Consulta de certificados por DNI: {dni}',
                metadata={
                    'dni': dni,
                    'results_count': len(certificates_list)
                },
                ip_address=get_client_ip(request)
            )
            
            context = self.get_context_data(**kwargs)
            context['form'] = form
            context['certificates'] = certificates_list
            context['dni'] = dni
            
            return self.render_to_response(context)
        
        # Si el formulario no es válido, mostrar errores
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class CertificateDownloadView(TemplateView):
    """Vista para descargar certificado PDF"""
    
    def get(self, request, uuid, *args, **kwargs):
        """Retorna el archivo PDF del certificado o redirige a URL externa"""
        from django.shortcuts import redirect
        
        # Buscar certificado por UUID
        certificate = get_object_or_404(Certificate, uuid=uuid)
        
        # Si es un certificado externo, redirigir a la URL externa
        if certificate.is_external and certificate.external_url:
            # Registrar acceso en AuditLog
            AuditLog.objects.create(
                action_type='QUERY',
                user=request.user if request.user.is_authenticated else None,
                description=f'Acceso a certificado externo: {certificate.participant.full_name}',
                metadata={
                    'certificate_uuid': str(certificate.uuid),
                    'external_url': certificate.external_url,
                    'external_system': certificate.external_system
                },
                ip_address=get_client_ip(request)
            )
            return redirect(certificate.external_url)
        
        # Verificar que el archivo existe para certificados internos
        if not certificate.pdf_file:
            raise Http404("El certificado no tiene un archivo PDF asociado")
        
        # Retornar archivo como descarga
        response = FileResponse(
            certificate.pdf_file.open('rb'),
            content_type='application/pdf'
        )
        
        # Configurar header para descarga
        filename = f"certificado_{certificate.participant.dni}_{certificate.uuid}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


@method_decorator(ratelimit(key='ip', rate='20/m', method='GET', block=True), name='get')
class CertificateVerificationView(DetailView):
    """Vista pública para verificar certificado mediante QR"""
    model = Certificate
    template_name = 'certificates/verify.html'
    context_object_name = 'certificate'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    
    def get_object(self, queryset=None):
        """Busca el certificado por UUID"""
        uuid = self.kwargs.get('uuid')
        
        try:
            certificate = Certificate.objects.select_related(
                'participant',
                'participant__event'
            ).get(uuid=uuid)
            
            # Registrar verificación en AuditLog
            AuditLog.objects.create(
                action_type='VERIFY',
                user=self.request.user if self.request.user.is_authenticated else None,
                description=f'Verificación de certificado: {uuid}',
                metadata={
                    'certificate_uuid': str(uuid),
                    'participant_dni': certificate.participant.dni,
                    'participant_name': certificate.participant.full_name,
                    'event_name': certificate.participant.event.name,
                    'is_signed': certificate.is_signed
                },
                ip_address=get_client_ip(self.request)
            )
            
            return certificate
            
        except Certificate.DoesNotExist:
            # Registrar intento de verificación fallido
            AuditLog.objects.create(
                action_type='VERIFY',
                user=self.request.user if self.request.user.is_authenticated else None,
                description=f'Intento de verificación de certificado inexistente: {uuid}',
                metadata={
                    'certificate_uuid': str(uuid),
                    'status': 'not_found'
                },
                ip_address=get_client_ip(self.request)
            )
            raise Http404("Certificado no encontrado")



# ============================================================================
# VISTA DE PREVIEW DE CERTIFICADOS CON QR
# ============================================================================

class CertificatePreviewView(TemplateView):
    """Vista pública para preview de certificados"""
    
    template_name = "certificates/preview.html"
    
    @method_decorator(ratelimit(key='ip', rate='30/m', method='GET'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, certificate_uuid):
        """
        Muestra el preview del certificado.
        
        Args:
            certificate_uuid: UUID del certificado
        """
        try:
            # Buscar certificado
            certificate = Certificate.objects.select_related(
                'participant', 'participant__event'
            ).get(uuid=certificate_uuid)
            
            # Verificar que esté listo para preview
            if not certificate.is_ready_for_preview():
                return render(
                    request,
                    'certificates/preview_not_ready.html',
                    {
                        'certificate': certificate,
                        'message': 'Este certificado aún no está disponible para visualización pública.'
                    },
                    status=403
                )
            
            # Registrar acceso en auditoría
            AuditLog.objects.create(
                action_type='VERIFY',
                description=f'Preview accedido para certificado {certificate_uuid}',
                metadata={
                    'certificate_uuid': str(certificate_uuid),
                    'participant_name': certificate.participant.full_name,
                    'participant_dni': certificate.participant.dni,
                },
                ip_address=get_client_ip(request)
            )
            
            # Preparar contexto
            context = {
                'certificate': certificate,
                'pdf_url': certificate.final_pdf.url if certificate.final_pdf else None,
                'verification_info': {
                    'participant_name': certificate.participant.full_name,
                    'dni': certificate.participant.dni,
                    'event_name': certificate.participant.event.name,
                    'event_date': certificate.participant.event.event_date,
                    'attendee_type': certificate.participant.get_attendee_type_display(),
                    'issue_date': certificate.generated_at,
                    'signed_date': certificate.signed_at,
                },
                'qr_code_url': certificate.qr_image.url if certificate.qr_image else None,
            }
            
            return render(request, self.template_name, context)
            
        except Certificate.DoesNotExist:
            return render(
                request,
                'certificates/preview_not_found.html',
                {
                    'uuid': certificate_uuid,
                    'message': 'El certificado solicitado no existe o no está disponible.'
                },
                status=404
            )
        except Exception as e:
            return render(
                request,
                'certificates/preview_error.html',
                {
                    'error': str(e),
                    'message': 'Ocurrió un error al cargar el certificado.'
                },
                status=500
            )
