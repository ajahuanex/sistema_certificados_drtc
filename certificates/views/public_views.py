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
        """Retorna el archivo PDF del certificado"""
        # Buscar certificado por UUID
        certificate = get_object_or_404(Certificate, uuid=uuid)
        
        # Verificar que el archivo existe
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
