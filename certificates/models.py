from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid


class CertificateTemplate(models.Model):
    """Plantilla para certificados"""
    name = models.CharField(max_length=200, verbose_name="Nombre")
    html_template = models.TextField(verbose_name="Plantilla HTML")
    css_styles = models.TextField(blank=True, verbose_name="Estilos CSS")
    background_image = models.ImageField(
        upload_to='templates/', 
        blank=True, 
        null=True,
        verbose_name="Imagen de fondo"
    )
    is_default = models.BooleanField(default=False, verbose_name="Plantilla por defecto")
    field_positions = models.JSONField(default=dict, verbose_name="Posiciones de campos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de Certificado"
        verbose_name_plural = "Plantillas de Certificados"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Si esta plantilla se marca como default, desmarcar las demás
        if self.is_default:
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Event(models.Model):
    """Evento de capacitación"""
    name = models.CharField(max_length=500, verbose_name="Nombre del evento")
    event_date = models.DateField(verbose_name="Fecha del evento")
    description = models.TextField(blank=True, verbose_name="Descripción")
    template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Plantilla"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.name} - {self.event_date.strftime('%d/%m/%Y')}"



class Participant(models.Model):
    """Participante de un evento"""
    ATTENDEE_TYPES = [
        ('ASISTENTE', 'Asistente'),
        ('PONENTE', 'Ponente'),
        ('ORGANIZADOR', 'Organizador'),
    ]

    dni = models.CharField(
        max_length=8,
        verbose_name="DNI",
        validators=[RegexValidator(r'^\d{8}$', 'DNI debe tener 8 dígitos numéricos')],
        db_index=True
    )
    full_name = models.CharField(max_length=300, verbose_name="Nombres y Apellidos")
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name="Evento"
    )
    attendee_type = models.CharField(
        max_length=20,
        choices=ATTENDEE_TYPES,
        verbose_name="Tipo de Asistente"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        unique_together = [['dni', 'event']]
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['dni', 'event']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.dni}) - {self.event.name}"



class Certificate(models.Model):
    """Certificado generado para un participante"""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="UUID"
    )
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE,
        related_name='certificate',
        verbose_name="Participante"
    )
    pdf_file = models.FileField(
        upload_to='certificates/%Y/%m/',
        verbose_name="Archivo PDF"
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/%Y/%m/',
        verbose_name="Código QR"
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Generado el")
    is_signed = models.BooleanField(default=False, verbose_name="Firmado digitalmente")
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="Firmado el")
    verification_url = models.URLField(verbose_name="URL de verificación")

    class Meta:
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
        ordering = ['-generated_at']

    def __str__(self):
        return f"Certificado {self.uuid} - {self.participant.full_name}"



class AuditLog(models.Model):
    """Registro de auditoría de acciones del sistema"""
    ACTION_TYPES = [
        ('IMPORT', 'Importación Excel'),
        ('GENERATE', 'Generación Certificado'),
        ('SIGN', 'Firma Digital'),
        ('QUERY', 'Consulta DNI'),
        ('VERIFY', 'Verificación QR'),
    ]

    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="Tipo de acción",
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    description = models.TextField(verbose_name="Descripción")
    metadata = models.JSONField(default=dict, verbose_name="Metadatos")
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora", db_index=True)

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action_type']),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
