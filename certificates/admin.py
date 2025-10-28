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
        "is_signed",
        "signed_status",
        "generated_at",
    ]
    list_filter = ["is_signed", "generated_at", "signed_at"]
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

    def signed_status(self, obj):
        """Estado de firma con color"""
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


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    """Administración de plantillas de certificados"""

    list_display = ["name", "is_default", "created_at", "updated_at"]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name"]
    ordering = ["-created_at"]


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
