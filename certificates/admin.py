from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Event,
    Participant,
    Certificate,
    CertificateTemplate,
    AuditLog,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Administración de eventos"""

    list_display = [
        "name",
        "event_date",
        "template",
        "participant_count",
        "created_at",
    ]
    list_filter = ["event_date", "created_at"]
    search_fields = ["name", "description"]
    date_hierarchy = "event_date"
    ordering = ["-event_date"]
    actions = ["generate_certificates_action"]

    def participant_count(self, obj):
        """Muestra el número de participantes"""
        return obj.participants.count()

    participant_count.short_description = "Participantes"

    @admin.action(description="Generar certificados para eventos seleccionados")
    def generate_certificates_action(self, request, queryset):
        """Genera certificados para todos los participantes de los eventos seleccionados"""
        from django.contrib import messages
        from certificates.services.certificate_generator import CertificateGeneratorService

        service = CertificateGeneratorService()
        total_success = 0
        total_errors = 0

        for event in queryset:
            result = service.generate_bulk_certificates(event, user=request.user)
            total_success += result["success_count"]
            total_errors += result["error_count"]

        if total_success > 0:
            self.message_user(
                request,
                f"✓ Se generaron {total_success} certificados exitosamente.",
                messages.SUCCESS,
            )

        if total_errors > 0:
            self.message_user(
                request,
                f"⚠ Se encontraron {total_errors} errores durante la generación.",
                messages.WARNING,
            )


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """Administración de participantes"""

    list_display = [
        "full_name",
        "dni",
        "event",
        "attendee_type",
        "has_certificate",
        "created_at",
    ]
    list_filter = ["attendee_type", "event", "created_at"]
    search_fields = ["full_name", "dni", "event__name"]
    ordering = ["-created_at"]
    raw_id_fields = ["event"]

    def has_certificate(self, obj):
        """Indica si el participante tiene certificado"""
        try:
            if obj.certificate:
                return format_html(
                    '<span style="color: green;">✓</span>'
                )
        except Certificate.DoesNotExist:
            pass
        return format_html('<span style="color: red;">✗</span>')

    has_certificate.short_description = "Certificado"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Administración de certificados"""

    list_display = [
        "uuid",
        "participant_name",
        "participant_dni",
        "event_name",
        "certificate_type",
        "signed_status",
        "generated_at",
    ]
    list_filter = ["is_signed", "is_external", "generated_at", "signed_at"]
    search_fields = [
        "uuid",
        "participant__full_name",
        "participant__dni",
        "participant__event__name",
    ]
    readonly_fields = [
        "uuid",
        "verification_url",
        "generated_at",
        "signed_at",
        "qr_code_preview",
    ]
    ordering = ["-generated_at"]
    raw_id_fields = ["participant"]
    actions = ["sign_certificates_action", "download_pdf_action"]

    def participant_name(self, obj):
        """Nombre del participante"""
        return obj.participant.full_name

    participant_name.short_description = "Participante"

    def participant_dni(self, obj):
        """DNI del participante"""
        return obj.participant.dni

    participant_dni.short_description = "DNI"

    def event_name(self, obj):
        """Nombre del evento"""
        return obj.participant.event.name

    event_name.short_description = "Evento"

    def certificate_type(self, obj):
        """Tipo de certificado (interno/externo)"""
        if obj.is_external:
            return format_html(
                '<span style="color: #6f42c1; font-weight: bold;">🔗 Externo</span>'
            )
        return format_html(
            '<span style="color: #007cba; font-weight: bold;">📄 Interno</span>'
        )
    
    certificate_type.short_description = "Tipo"
    
    def signed_status(self, obj):
        """Estado de firma con color"""
        if obj.is_external:
            return format_html(
                '<span style="color: #6c757d;">N/A (Externo)</span>'
            )
        if obj.is_signed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Firmado</span>'
            )
        return format_html(
            '<span style="color: orange;">⏳ Sin firmar</span>'
        )

    signed_status.short_description = "Estado"

    def qr_code_preview(self, obj):
        """Muestra preview del código QR"""
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="150" height="150" />',
                obj.qr_code.url,
            )
        return "No disponible"

    qr_code_preview.short_description = "Código QR"

    @admin.action(description="Firmar certificados seleccionados")
    def sign_certificates_action(self, request, queryset):
        """Firma digitalmente los certificados seleccionados"""
        from django.contrib import messages
        from certificates.services.digital_signature import DigitalSignatureService

        service = DigitalSignatureService()
        result = service.sign_bulk_certificates(queryset, user=request.user)

        if result["success_count"] > 0:
            self.message_user(
                request,
                f"✓ Se firmaron {result['success_count']} certificados exitosamente.",
                messages.SUCCESS,
            )

        if result["error_count"] > 0:
            self.message_user(
                request,
                f"⚠ Se encontraron {result['error_count']} errores durante la firma.",
                messages.WARNING,
            )

            # Mostrar primeros 3 errores
            for error in result["errors"][:3]:
                self.message_user(request, error, messages.ERROR)

    @admin.action(description="Descargar PDF de certificados seleccionados")
    def download_pdf_action(self, request, queryset):
        """Descarga los PDFs de los certificados seleccionados como ZIP"""
        from django.http import HttpResponse
        from django.contrib import messages
        import zipfile
        from io import BytesIO

        if queryset.count() == 1:
            # Si es solo un certificado, descargar directamente
            certificate = queryset.first()
            response = HttpResponse(
                certificate.pdf_file.read(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="certificado_{certificate.participant.dni}.pdf"'
            )
            return response

        # Si son múltiples, crear ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for certificate in queryset:
                if certificate.pdf_file:
                    certificate.pdf_file.seek(0)
                    filename = f"certificado_{certificate.participant.dni}_{certificate.uuid}.pdf"
                    zip_file.writestr(filename, certificate.pdf_file.read())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="certificados.zip"'

        self.message_user(
            request,
            f"✓ Se descargaron {queryset.count()} certificados.",
            messages.SUCCESS,
        )

        return response
    
    def changelist_view(self, request, extra_context=None):
        """Agrega contexto adicional a la vista de lista"""
        extra_context = extra_context or {}
        extra_context['import_external_url'] = '/admin/import-external/'
        extra_context['import_excel_url'] = '/admin/import-excel/'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    """Administración de plantillas de certificados"""

    list_display = ["name", "is_default", "preview_link", "created_at", "updated_at"]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name"]
    ordering = ["-created_at"]
    readonly_fields = ["preview_button", "created_at", "updated_at"]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'is_default')
        }),
        ('Plantilla HTML', {
            'fields': ('html_template',),
            'description': 'Código HTML de la plantilla del certificado'
        }),
        ('Vista Previa', {
            'fields': ('preview_button',),
            'description': 'Previsualiza cómo se verá el certificado con datos de ejemplo'
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_link(self, obj):
        """Enlace para previsualizar la plantilla"""
        from django.urls import reverse
        url = reverse('admin:certificates_certificatetemplate_preview', args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" class="button">👁️ Vista Previa</a>',
            url
        )
    preview_link.short_description = "Acciones"
    
    def preview_button(self, obj):
        """Botón de preview en el formulario de edición"""
        if obj.pk:
            from django.urls import reverse
            url = reverse('admin:certificates_certificatetemplate_preview', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" class="button" style="padding: 10px 15px; background-color: #417690; color: white; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">👁️ Ver Vista Previa del Certificado</a>',
                url
            )
        return "Guarda la plantilla primero para ver la vista previa"
    preview_button.short_description = "Vista Previa"
    
    def get_urls(self):
        """Agregar URL personalizada para preview"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:template_id>/preview/',
                self.admin_site.admin_view(self.preview_template),
                name='certificates_certificatetemplate_preview',
            ),
        ]
        return custom_urls + urls
    
    def preview_template(self, request, template_id):
        """Vista para previsualizar la plantilla"""
        from django.shortcuts import get_object_or_404
        from django.http import HttpResponse
        from certificates.services.certificate_generator import CertificateGeneratorService
        from certificates.services.qr_service import QRCodeService
        from datetime import date
        import uuid
        
        template = get_object_or_404(CertificateTemplate, pk=template_id)
        
        # Datos de ejemplo para el preview
        sample_uuid = str(uuid.uuid4())
        verification_url = f'https://certificados.drtcpuno.gob.pe/verificar/{sample_uuid}'
        
        sample_data = {
            'full_name': 'JUAN PÉREZ GARCÍA',
            'dni': '12345678',
            'event_name': 'Capacitación en Seguridad Vial 2024',
            'event_date': date.today().strftime('%d de %B de %Y'),
            'attendee_type': 'ASISTENTE',
            'verification_url': verification_url,
        }
        
        # Generar PDF de ejemplo
        try:
            service = CertificateGeneratorService()
            qr_service = QRCodeService()
            
            # Generar QR code de ejemplo con la URL completa
            qr_buffer = qr_service.generate_qr(verification_url)
            
            # Generar PDF
            pdf_bytes = service._create_pdf(sample_data, template, qr_buffer)
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="preview_{template.name}.pdf"'
            return response
        except Exception as e:
            import traceback
            error_html = f"""
            <html>
            <head>
                <title>Error en Preview</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .error-container {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #c62828;
                        border-bottom: 3px solid #c62828;
                        padding-bottom: 10px;
                    }}
                    .error-message {{
                        background: #ffebee;
                        color: #b71c1c;
                        padding: 15px;
                        border-radius: 4px;
                        margin: 20px 0;
                        border-left: 4px solid #c62828;
                    }}
                    pre {{
                        background: #263238;
                        color: #aed581;
                        padding: 15px;
                        border-radius: 4px;
                        overflow-x: auto;
                        font-size: 12px;
                    }}
                    .back-button {{
                        display: inline-block;
                        background: #1565c0;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-top: 20px;
                    }}
                    .back-button:hover {{
                        background: #0d47a1;
                    }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>❌ Error al generar vista previa</h1>
                    <div class="error-message">
                        <strong>Error:</strong> {str(e)}
                    </div>
                    <h3>Detalles técnicos:</h3>
                    <pre>{traceback.format_exc()}</pre>
                    <a href="javascript:history.back()" class="back-button">← Volver</a>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_html, status=500)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Administración de registros de auditoría (solo lectura)"""

    list_display = [
        "timestamp",
        "action_type",
        "user",
        "description",
        "ip_address",
    ]
    list_filter = ["action_type", "timestamp"]
    search_fields = ["description", "user__username", "ip_address"]
    readonly_fields = [
        "action_type",
        "user",
        "description",
        "metadata",
        "ip_address",
        "timestamp",
    ]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False

    def has_change_permission(self, request, obj=None):
        """Permitir ver pero no editar"""
        return request.method in ["GET", "HEAD"]

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros"""
        return False
