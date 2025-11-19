from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import (
    Event,
    Participant,
    Certificate,
    CertificateTemplate,
    TemplateElement,
    TemplateAsset,
    AuditLog,
    QRProcessingConfig,
)


# Configuración global de Media para todos los admins
class BaseAdmin(admin.ModelAdmin):
    """Base admin con CSS personalizado"""
    class Media:
        css = {
            'all': (
                'admin/css/custom_admin.css',
                'admin/css/fix-header-contrast.css',  # FIX CRÍTICO - Se carga al final
            )
        }


@admin.register(Event)
class EventAdmin(BaseAdmin):
    """Administración de eventos"""

    list_display = [
        "name",
        "event_date",
        "template_info",
        "participant_count",
        "created_at",
    ]
    list_filter = ["event_date", "created_at"]
    search_fields = ["name", "description"]
    date_hierarchy = "event_date"
    ordering = ["-event_date"]
    actions = ["generate_certificates_action"]

    def template_info(self, obj):
        """Muestra información de la plantilla"""
        if obj.template:
            template_type = "🎨 Visual" if obj.template.elements.exists() else "📝 HTML"
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.template.name,
                template_type
            )
        return format_html('<em style="color: #999;">Sin plantilla</em>')
    
    template_info.short_description = "Plantilla"

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
class ParticipantAdmin(BaseAdmin):
    """Administración de participantes"""

    list_display = [
        "full_name",
        "dni",
        "event",
        "attendee_type",
        "has_certificate",
        "created_at",
        "quick_actions",
    ]
    list_filter = ["attendee_type", "event", "created_at"]
    search_fields = ["full_name", "dni", "event__name"]
    ordering = ["-created_at"]
    raw_id_fields = ["event"]
    list_editable = ["attendee_type"]
    actions = ["generate_certificates_for_participants", "delete_selected_participants"]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('dni', 'full_name')
        }),
        ('Evento', {
            'fields': ('event', 'attendee_type')
        }),
        ('Información del Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_certificate(self, obj):
        """Indica si el participante tiene certificado"""
        try:
            if obj.certificate:
                cert_url = f'/admin/certificates/certificate/{obj.certificate.pk}/change/'
                return format_html(
                    '<a href="{}" style="color: green; font-weight: bold;">✓ Ver</a>',
                    cert_url
                )
        except Certificate.DoesNotExist:
            pass
        return format_html('<span style="color: #999;">✗ Sin certificado</span>')

    has_certificate.short_description = "Certificado"
    
    def quick_actions(self, obj):
        """Acciones rápidas para cada participante"""
        from django.urls import reverse
        
        actions = []
        
        # Botón de editar
        edit_url = reverse('admin:certificates_participant_change', args=[obj.pk])
        actions.append(f'<a href="{edit_url}" class="button" style="font-size: 11px; padding: 3px 8px;">✏️</a>')
        
        # Botón de eliminar
        delete_url = reverse('admin:certificates_participant_delete', args=[obj.pk])
        actions.append(f'<a href="{delete_url}" class="button" style="font-size: 11px; padding: 3px 8px; background-color: #dc3545; color: white;">🗑️</a>')
        
        # Botón de generar certificado si no tiene
        try:
            obj.certificate
        except Certificate.DoesNotExist:
            actions.append('<span style="font-size: 11px; color: #999;">📄 Sin cert.</span>')
        
        return format_html(' '.join(actions))
    
    quick_actions.short_description = "Acciones"
    
    @admin.action(description="📄 Generar certificados para participantes seleccionados")
    def generate_certificates_for_participants(self, request, queryset):
        """Genera certificados para los participantes seleccionados"""
        from django.contrib import messages
        from certificates.services.certificate_generator import CertificateGeneratorService
        
        service = CertificateGeneratorService()
        success_count = 0
        error_count = 0
        
        for participant in queryset:
            # Verificar si ya tiene certificado
            try:
                participant.certificate
                error_count += 1
                continue
            except Certificate.DoesNotExist:
                pass
            
            # Generar certificado
            result = service.generate_certificate(participant, user=request.user)
            if result['success']:
                success_count += 1
            else:
                error_count += 1
        
        if success_count > 0:
            self.message_user(
                request,
                f"✓ Se generaron {success_count} certificados exitosamente",
                messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f"⚠ {error_count} participantes ya tenían certificado o hubo errores",
                messages.WARNING
            )
    
    @admin.action(description="🗑️ Eliminar participantes seleccionados")
    def delete_selected_participants(self, request, queryset):
        """Elimina los participantes seleccionados"""
        from django.contrib import messages
        
        count = queryset.count()
        queryset.delete()
        
        self.message_user(
            request,
            f"✓ Se eliminaron {count} participantes exitosamente",
            messages.SUCCESS
        )
    
    def get_actions(self, request):
        """Personalizar acciones disponibles"""
        actions = super().get_actions(request)
        # Remover la acción de eliminar por defecto de Django
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Certificate)
class CertificateAdmin(BaseAdmin):
    """Administración de certificados"""

    list_display = [
        "uuid_short",
        "participant_name",
        "participant_dni",
        "event_name",
        "certificate_type",
        "signed_status",
        "generated_at",
        "quick_actions",
    ]
    list_filter = ["is_signed", "is_external", "generated_at", "signed_at", "processing_status"]
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
        "pdf_preview",
    ]
    ordering = ["-generated_at"]
    raw_id_fields = ["participant"]
    actions = [
        "sign_certificates_action",
        "download_pdf_action",
        "process_qr_action",
        "export_for_signing_action",
        "delete_selected_certificates",
        "mark_as_external",
        "mark_as_internal",
    ]
    
    fieldsets = (
        ('Información del Certificado', {
            'fields': ('uuid', 'participant', 'verification_url')
        }),
        ('Tipo de Certificado', {
            'fields': ('is_external', 'external_url', 'external_system'),
            'description': 'Marcar como externo si el certificado está alojado en otro sistema'
        }),
        ('Archivos', {
            'fields': ('pdf_file', 'qr_code', 'pdf_preview', 'qr_code_preview')
        }),
        ('Estado de Firma', {
            'fields': ('is_signed', 'signed_at')
        }),
        ('Procesamiento QR', {
            'fields': ('processing_status', 'original_pdf', 'qr_pdf', 'final_pdf', 'qr_image'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def uuid_short(self, obj):
        """Muestra UUID acortado"""
        return format_html(
            '<code style="font-size: 11px;">{}</code>',
            str(obj.uuid)[:8]
        )
    uuid_short.short_description = "UUID"

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
    
    def pdf_preview(self, obj):
        """Muestra enlace para ver el PDF"""
        if obj.is_external and obj.external_url:
            return format_html(
                '<a href="{}" target="_blank" class="button">🔗 Ver Certificado Externo</a>',
                obj.external_url
            )
        elif obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">📄 Ver PDF</a>',
                obj.pdf_file.url
            )
        return "No disponible"
    
    pdf_preview.short_description = "Vista Previa"
    
    def quick_actions(self, obj):
        """Acciones rápidas para cada certificado"""
        from django.urls import reverse
        
        actions = []
        
        # Botón de editar
        edit_url = reverse('admin:certificates_certificate_change', args=[obj.pk])
        actions.append(f'<a href="{edit_url}" class="button" style="font-size: 11px; padding: 3px 8px;">✏️</a>')
        
        # Botón de eliminar
        delete_url = reverse('admin:certificates_certificate_delete', args=[obj.pk])
        actions.append(f'<a href="{delete_url}" class="button" style="font-size: 11px; padding: 3px 8px; background-color: #dc3545; color: white;">🗑️</a>')
        
        # Botón de ver
        if obj.is_external and obj.external_url:
            actions.append(f'<a href="{obj.external_url}" target="_blank" class="button" style="font-size: 11px; padding: 3px 8px;">👁️</a>')
        elif obj.pdf_file:
            actions.append(f'<a href="{obj.pdf_file.url}" target="_blank" class="button" style="font-size: 11px; padding: 3px 8px;">👁️</a>')
        
        return format_html(' '.join(actions))
    
    quick_actions.short_description = "Acciones"

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
    
    @admin.action(description="🔄 Procesar QR para certificados seleccionados")
    def process_qr_action(self, request, queryset):
        """Procesa QR para certificados seleccionados"""
        from django.http import HttpResponse
        from certificates.services.pdf_processing import PDFProcessingService
        from certificates.models import QRProcessingConfig
        
        # Filtrar solo certificados que pueden procesarse
        valid_certs = queryset.filter(processing_status='IMPORTED')
        
        if not valid_certs.exists():
            self.message_user(
                request,
                "⚠ No hay certificados válidos para procesar (deben estar en estado IMPORTED)",
                messages.WARNING
            )
            return
        
        # Obtener configuración
        config = QRProcessingConfig.get_active_config()
        
        # Procesar cada certificado
        service = PDFProcessingService()
        success_count = 0
        error_count = 0
        errors = []
        
        for certificate in valid_certs:
            result = service.process_qr_for_certificate(certificate, config)
            
            if result['success']:
                success_count += 1
            else:
                error_count += 1
                errors.append(f"{certificate.participant.full_name}: {result['error']}")
        
        # Mostrar resultados
        if success_count > 0:
            self.message_user(
                request,
                f"✓ Se procesaron {success_count} certificados exitosamente",
                messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f"⚠ Se encontraron {error_count} errores",
                messages.WARNING
            )
            for error in errors[:5]:
                self.message_user(request, error, messages.ERROR)
    
    @admin.action(description="📤 Exportar para firma digital")
    def export_for_signing_action(self, request, queryset):
        """Exporta certificados para firma digital"""
        from django.http import HttpResponse
        from certificates.services.pdf_processing import PDFProcessingService
        
        # Filtrar solo certificados que pueden exportarse
        valid_certs = queryset.filter(processing_status='QR_INSERTED')
        
        if not valid_certs.exists():
            self.message_user(
                request,
                "⚠ No hay certificados válidos para exportar (deben estar en estado QR_INSERTED)",
                messages.WARNING
            )
            return
        
        # Crear ZIP
        service = PDFProcessingService()
        try:
            zip_bytes, zip_filename = service.create_export_zip(
                certificates=list(valid_certs),
                include_metadata=True
            )
            
            # Retornar ZIP como descarga
            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            
            self.message_user(
                request,
                f"✓ Se exportaron {valid_certs.count()} certificados",
                messages.SUCCESS
            )
            
            return response
            
        except Exception as e:
            self.message_user(
                request,
                f"❌ Error al crear ZIP: {str(e)}",
                messages.ERROR
            )
    
    @admin.action(description="🗑️ Eliminar certificados seleccionados")
    def delete_selected_certificates(self, request, queryset):
        """Elimina los certificados seleccionados"""
        from django.contrib import messages
        
        count = queryset.count()
        queryset.delete()
        
        self.message_user(
            request,
            f"✓ Se eliminaron {count} certificados exitosamente",
            messages.SUCCESS
        )
    
    @admin.action(description="🔗 Marcar como certificados externos")
    def mark_as_external(self, request, queryset):
        """Marca los certificados seleccionados como externos"""
        from django.contrib import messages
        
        count = queryset.update(is_external=True)
        
        self.message_user(
            request,
            f"✓ Se marcaron {count} certificados como externos",
            messages.SUCCESS
        )
    
    @admin.action(description="📄 Marcar como certificados internos")
    def mark_as_internal(self, request, queryset):
        """Marca los certificados seleccionados como internos"""
        from django.contrib import messages
        
        count = queryset.update(is_external=False, external_url='', external_system='')
        
        self.message_user(
            request,
            f"✓ Se marcaron {count} certificados como internos",
            messages.SUCCESS
        )
    
    def get_actions(self, request):
        """Personalizar acciones disponibles"""
        actions = super().get_actions(request)
        # Remover la acción de eliminar por defecto de Django
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def changelist_view(self, request, extra_context=None):
        """Agrega contexto adicional a la vista de lista"""
        extra_context = extra_context or {}
        
        # Contar plantillas que pueden migrarse
        templates_to_migrate = CertificateTemplate.objects.filter(elements__isnull=True).distinct().count()
        extra_context['templates_to_migrate'] = templates_to_migrate
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(BaseAdmin):
    """Administración de plantillas de certificados"""

    list_display = ["name", "is_default", "template_type", "editor_actions", "preview_link", "created_at", "updated_at"]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name"]
    ordering = ["-created_at"]
    readonly_fields = ["preview_button", "created_at", "updated_at"]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'is_default')
        }),
        ('Dimensiones del Canvas', {
            'fields': ('canvas_width', 'canvas_height'),
            'description': 'A4 Horizontal: 842×595px | A4 Vertical: 595×842px | Carta: 792×612px'
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
    
    def template_type(self, obj):
        """Muestra el tipo de plantilla (visual o HTML)"""
        if hasattr(obj, 'elements') and obj.elements.exists():
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">🎨 Visual</span>'
            )
        return format_html(
            '<span style="color: #6c757d;">📝 HTML</span>'
        )
    template_type.short_description = "Tipo"

    def editor_actions(self, obj):
        """Enlaces para editar la plantilla"""
        from django.urls import reverse
        
        # Link al editor visual
        visual_editor_url = reverse('certificates:template_editor', args=[obj.pk])
        
        # Link al admin normal
        admin_edit_url = reverse('admin:certificates_certificatetemplate_change', args=[obj.pk])
        
        # Link de migración si no tiene elementos visuales
        migrate_button = ''
        if not obj.elements.exists():
            migrate_url = reverse('admin:certificates_certificatetemplate_migrate', args=[obj.pk])
            migrate_button = f'<a href="{migrate_url}" class="button" style="margin-right: 5px; background-color: #ffc107; color: #000;">🔄 Migrar</a>'
        
        return format_html(
            '{}<a href="{}" class="button" style="margin-right: 5px;">🎨 Editor Visual</a>'
            '<a href="{}" class="button">✏️ Editar HTML</a>',
            migrate_button,
            visual_editor_url,
            admin_edit_url
        )
    editor_actions.short_description = "Editar"

    def preview_link(self, obj):
        """Enlace para previsualizar la plantilla"""
        from django.urls import reverse
        url = reverse('admin:certificates_certificatetemplate_preview', args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" class="button">👁️ Vista Previa</a>',
            url
        )
    preview_link.short_description = "Vista Previa"
    
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
        """Agregar URLs personalizadas"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:template_id>/preview/',
                self.admin_site.admin_view(self.preview_template),
                name='certificates_certificatetemplate_preview',
            ),
            path(
                '<int:template_id>/migrate/',
                self.admin_site.admin_view(self.migrate_template),
                name='certificates_certificatetemplate_migrate',
            ),
            path(
                'migrate-all/',
                self.admin_site.admin_view(self.migrate_all_templates),
                name='certificates_certificatetemplate_migrate_all',
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
    
    def migrate_template(self, request, template_id):
        """Vista para migrar una plantilla individual al formato visual"""
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        from certificates.services.template_migration import TemplateMigrationService
        
        template = get_object_or_404(CertificateTemplate, pk=template_id)
        
        if request.method == 'POST':
            # Realizar migración
            service = TemplateMigrationService()
            result = service.migrate_template(template_id, preserve_original=True)
            
            if result['success']:
                messages.success(
                    request,
                    f'✓ Plantilla "{template.name}" migrada exitosamente con {result["elements_created"]} elementos'
                )
            else:
                messages.error(
                    request,
                    f'✗ Error migrando plantilla: {result["error"]}'
                )
            
            return redirect('admin:certificates_certificatetemplate_changelist')
        
        # Mostrar preview de migración
        service = TemplateMigrationService()
        preview_result = service.preview_migration(template_id)
        
        context = {
            'title': f'Migrar Plantilla: {template.name}',
            'template': template,
            'preview_result': preview_result,
            'opts': CertificateTemplate._meta,
        }
        
        return render(request, 'admin/certificates/migrate_template.html', context)
    
    def migrate_all_templates(self, request):
        """Vista para migrar todas las plantillas al formato visual"""
        from django.shortcuts import redirect
        from django.contrib import messages
        from certificates.services.template_migration import TemplateMigrationService
        
        if request.method == 'POST':
            # Realizar migración masiva
            service = TemplateMigrationService()
            results = service.migrate_all_templates(exclude_with_elements=True)
            
            if results['migrated_successfully'] > 0:
                messages.success(
                    request,
                    f'✓ {results["migrated_successfully"]} plantillas migradas exitosamente'
                )
            
            if results['migration_errors'] > 0:
                messages.warning(
                    request,
                    f'⚠ {results["migration_errors"]} plantillas tuvieron errores'
                )
                
                # Mostrar algunos errores
                for error in results['errors'][:3]:
                    messages.error(
                        request,
                        f'Error en "{error["template_name"]}": {error["error"]}'
                    )
            
            return redirect('admin:certificates_certificatetemplate_changelist')
        
        # Mostrar preview de migración masiva
        service = TemplateMigrationService()
        templates = CertificateTemplate.objects.filter(elements__isnull=True).distinct()
        
        preview_results = []
        for template in templates[:10]:  # Mostrar solo los primeros 10
            preview = service.preview_migration(template.id)
            preview_results.append({
                'template': template,
                'preview': preview
            })
        
        context = {
            'title': 'Migrar Todas las Plantillas',
            'total_templates': templates.count(),
            'preview_results': preview_results,
            'opts': CertificateTemplate._meta,
        }
        
        return render(request, 'admin/certificates/migrate_all_templates.html', context)


@admin.register(AuditLog)
class AuditLogAdmin(BaseAdmin):
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



@admin.register(QRProcessingConfig)
class QRProcessingConfigAdmin(BaseAdmin):
    """Administración de configuraciones de procesamiento QR"""

    list_display = [
        "name",
        "is_active_badge",
        "qr_position_display",
        "qr_size_display",
        "preview_url_display",
        "updated_at",
    ]
    list_filter = ["is_active", "qr_error_correction", "created_at"]
    search_fields = ["name", "description", "preview_base_url"]
    readonly_fields = ["created_at", "updated_at", "created_by"]
    ordering = ["-is_active", "-created_at"]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Posicionamiento del QR', {
            'fields': ('default_qr_x', 'default_qr_y', 'default_qr_size'),
            'description': 'Configuración de la posición y tamaño del código QR en el PDF'
        }),
        ('Calidad del QR', {
            'fields': ('qr_error_correction', 'qr_border', 'qr_box_size'),
            'description': 'Configuración de calidad y apariencia del código QR'
        }),
        ('URL de Preview', {
            'fields': ('preview_base_url',),
            'description': 'URL base que se usará en los códigos QR para acceder al preview'
        }),
        ('Opciones de Procesamiento', {
            'fields': ('enable_qr_validation', 'enable_pdf_backup', 'max_pdf_size_mb'),
            'description': 'Opciones adicionales para el procesamiento de certificados'
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def is_active_badge(self, obj):
        """Muestra un badge visual del estado activo"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">✓ Activa</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 12px;">✗ Inactiva</span>'
        )
    
    is_active_badge.short_description = "Estado"

    def qr_position_display(self, obj):
        """Muestra la posición del QR de forma legible"""
        return f"({obj.default_qr_x}, {obj.default_qr_y})"
    
    qr_position_display.short_description = "Posición QR"

    def qr_size_display(self, obj):
        """Muestra el tamaño del QR"""
        return f"{obj.default_qr_size}px"
    
    qr_size_display.short_description = "Tamaño QR"

    def preview_url_display(self, obj):
        """Muestra la URL base de forma truncada"""
        url = obj.preview_base_url
        if len(url) > 40:
            return f"{url[:37]}..."
        return url
    
    preview_url_display.short_description = "URL Base"

    def save_model(self, request, obj, form, change):
        """Guarda el modelo y registra quién lo creó"""
        if not change:  # Si es nuevo
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar si es la única configuración activa"""
        if obj and obj.is_active:
            # Verificar si es la única configuración activa
            active_count = QRProcessingConfig.objects.filter(is_active=True).count()
            if active_count <= 1:
                return False
        return super().has_delete_permission(request, obj)



# ============================================================================
# ADMIN PARA EDITOR DE PLANTILLAS AVANZADO
# ============================================================================

class TemplateElementInline(admin.TabularInline):
    """Inline para elementos de plantilla"""
    model = TemplateElement
    extra = 0
    fields = ['name', 'element_type', 'position_x', 'position_y', 'width', 'height', 'z_index', 'is_visible']
    readonly_fields = []
    ordering = ['z_index']


@admin.register(TemplateAsset)
class TemplateAssetAdmin(BaseAdmin):
    """Administración de assets de plantillas"""
    
    list_display = [
        'name',
        'asset_type_badge',
        'category',
        'preview_thumbnail',
        'is_public_badge',
        'created_by',
        'created_at',
    ]
    list_filter = ['asset_type', 'category', 'is_public', 'created_at']
    search_fields = ['name', 'category']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'preview_image']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'asset_type', 'category', 'is_public')
        }),
        ('Archivo', {
            'fields': ('file', 'preview_image'),
            'description': 'Formatos permitidos: PNG, JPG, JPEG, SVG (máx 10MB)'
        }),
        ('Información del Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def asset_type_badge(self, obj):
        """Muestra el tipo de asset con color"""
        colors = {
            'BACKGROUND': '#007bff',
            'LOGO': '#28a745',
            'SIGNATURE': '#ffc107',
            'SEAL': '#dc3545',
            'ICON': '#6c757d',
        }
        color = colors.get(obj.asset_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            obj.get_asset_type_display()
        )
    
    asset_type_badge.short_description = "Tipo"
    
    def is_public_badge(self, obj):
        """Muestra si el asset es público"""
        if obj.is_public:
            return format_html(
                '<span style="color: #28a745;">✓ Público</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Privado</span>'
        )
    
    is_public_badge.short_description = "Visibilidad"
    
    def preview_thumbnail(self, obj):
        """Muestra miniatura del asset"""
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px;" />',
                obj.file.url
            )
        return "-"
    
    preview_thumbnail.short_description = "Vista Previa"
    
    def preview_image(self, obj):
        """Muestra imagen completa en el formulario"""
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />',
                obj.file.url
            )
        return "No hay imagen disponible"
    
    preview_image.short_description = "Vista Previa Completa"
    
    def save_model(self, request, obj, form, change):
        """Guarda el modelo y registra quién lo creó"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """Verificar si el asset está en uso antes de eliminar"""
        if obj:
            # Verificar si está siendo usado como fondo en alguna plantilla
            if obj.templates_using_as_background.exists():
                return False
            # Verificar si está siendo usado en algún elemento
            if obj.elements_using.exists():
                return False
        return super().has_delete_permission(request, obj)


@admin.register(TemplateElement)
class TemplateElementAdmin(BaseAdmin):
    """Administración de elementos de plantillas"""
    
    list_display = [
        'name',
        'template',
        'element_type_badge',
        'position_display',
        'size_display',
        'z_index',
        'is_visible_badge',
        'is_locked_badge',
    ]
    list_filter = ['element_type', 'template', 'is_visible', 'is_locked']
    search_fields = ['name', 'content', 'template__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['template', 'z_index']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('template', 'element_type', 'name')
        }),
        ('Posicionamiento', {
            'fields': (
                ('position_x', 'position_y'),
                ('width', 'height'),
                'rotation',
                'z_index'
            ),
            'description': 'Posición y dimensiones del elemento en el canvas'
        }),
        ('Contenido', {
            'fields': ('content', 'asset', 'variables'),
            'description': 'Contenido del elemento (texto, LaTeX, o referencia a asset)'
        }),
        ('Estilo', {
            'fields': ('style_config',),
            'description': 'Configuración de estilo en formato JSON'
        }),
        ('Opciones', {
            'fields': ('is_visible', 'is_locked'),
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def element_type_badge(self, obj):
        """Muestra el tipo de elemento con color"""
        colors = {
            'TEXT': '#007bff',
            'IMAGE': '#28a745',
            'QR': '#ffc107',
            'LATEX': '#dc3545',
            'VARIABLE': '#6c757d',
        }
        color = colors.get(obj.element_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            obj.get_element_type_display()
        )
    
    element_type_badge.short_description = "Tipo"
    
    def position_display(self, obj):
        """Muestra la posición de forma legible"""
        return f"({obj.position_x}, {obj.position_y})"
    
    position_display.short_description = "Posición"
    
    def size_display(self, obj):
        """Muestra el tamaño de forma legible"""
        return f"{obj.width}×{obj.height}px"
    
    size_display.short_description = "Tamaño"
    
    def is_visible_badge(self, obj):
        """Muestra si el elemento es visible"""
        if obj.is_visible:
            return format_html('<span style="color: #28a745;">✓</span>')
        return format_html('<span style="color: #dc3545;">✗</span>')
    
    is_visible_badge.short_description = "Visible"
    
    def is_locked_badge(self, obj):
        """Muestra si el elemento está bloqueado"""
        if obj.is_locked:
            return format_html('<span style="color: #ffc107;">🔒</span>')
        return format_html('<span style="color: #28a745;">🔓</span>')
    
    is_locked_badge.short_description = "Bloqueado"


# Actualizar el admin de CertificateTemplate para incluir los elementos inline
# Primero, desregistrar el admin existente si está registrado
try:
    admin.site.unregister(CertificateTemplate)
except admin.sites.NotRegistered:
    pass

@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(BaseAdmin):
    """Administración de plantillas de certificados con editor visual"""
    
    list_display = [
        'name',
        'is_default_badge',
        'canvas_dimensions',
        'element_count',
        'editor_version',
        'last_edited_by',
        'updated_at',
    ]
    list_filter = ['is_default', 'editor_version', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_default', '-updated_at']
    inlines = [TemplateElementInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'is_default')
        }),
        ('Plantilla HTML (Sistema Antiguo)', {
            'fields': ('html_template', 'css_styles', 'background_image', 'field_positions'),
            'classes': ('collapse',),
            'description': 'Campos del sistema antiguo de plantillas HTML'
        }),
        ('Editor Visual', {
            'fields': (
                ('canvas_width', 'canvas_height'),
                'background_asset',
                'render_config',
                'available_variables',
                'editor_version',
                'last_edited_by'
            ),
            'description': 'Configuración del editor visual avanzado'
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_default_badge(self, obj):
        """Muestra si es la plantilla por defecto"""
        if obj.is_default:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">★ Por Defecto</span>'
            )
        return format_html(
            '<span style="color: #6c757d;">-</span>'
        )
    
    is_default_badge.short_description = "Estado"
    
    def canvas_dimensions(self, obj):
        """Muestra las dimensiones del canvas"""
        return f"{obj.canvas_width}×{obj.canvas_height}px"
    
    canvas_dimensions.short_description = "Dimensiones"
    
    def element_count(self, obj):
        """Muestra el número de elementos en la plantilla"""
        count = obj.elements.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">{}</span>',
                count
            )
        return "-"
    
    element_count.short_description = "Elementos"
    
    def save_model(self, request, obj, form, change):
        """Guarda el modelo y registra quién lo editó"""
        obj.last_edited_by = request.user
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        """Personaliza respuesta después de agregar"""
        if '_visual_editor' in request.POST:
            return redirect('certificates:template_editor', template_id=obj.id)
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """Personaliza respuesta después de cambiar"""
        if '_visual_editor' in request.POST:
            return redirect('certificates:template_editor', template_id=obj.id)
        return super().response_change(request, obj)
    
    def get_urls(self):
        """Agrega URLs personalizadas"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/visual-editor/',
                self.admin_site.admin_view(self.visual_editor_view),
                name='certificates_certificatetemplate_visual_editor'
            ),
        ]
        return custom_urls + urls
    
    def visual_editor_view(self, request, object_id):
        """Vista para abrir el editor visual"""
        from django.shortcuts import redirect
        return redirect('certificates:template_editor', template_id=object_id)
