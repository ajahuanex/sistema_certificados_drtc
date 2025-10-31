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
    """
    Certificado generado para un participante.
    
    Índices de base de datos:
    - is_external: Para filtrar certificados internos vs externos
    - generated_at: Para ordenar y filtrar por fecha (usado en dashboard)
    - is_signed: Para filtrar certificados firmados vs sin firmar (usado en dashboard)
    """
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
        verbose_name="Archivo PDF",
        blank=True,
        null=True
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/%Y/%m/',
        verbose_name="Código QR",
        blank=True,
        null=True
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Generado el")
    is_signed = models.BooleanField(default=False, verbose_name="Firmado digitalmente")
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="Firmado el")
    verification_url = models.URLField(verbose_name="URL de verificación", blank=True)
    
    # Campos para certificados externos
    is_external = models.BooleanField(
        default=False,
        verbose_name="Certificado Externo",
        help_text="Indica si el certificado fue importado de un sistema externo"
    )
    external_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL Externa",
        help_text="URL del certificado en el sistema externo"
    )
    external_system = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sistema Externo",
        help_text="Nombre del sistema del que proviene el certificado"
    )
    
    # ============================================================================
    # CAMPOS PARA PROCESAMIENTO DE PDFs CON QR
    # ============================================================================
    
    # Estado de procesamiento
    PROCESSING_STATUS_CHOICES = [
        ('IMPORTED', 'Importado (sin QR)'),
        ('QR_GENERATED', 'QR Generado'),
        ('QR_INSERTED', 'QR Insertado en PDF'),
        ('EXPORTED_FOR_SIGNING', 'Exportado para Firma'),
        ('SIGNED_FINAL', 'Firmado Final'),
        ('ERROR', 'Error en Procesamiento'),
    ]
    
    processing_status = models.CharField(
        max_length=50,
        choices=PROCESSING_STATUS_CHOICES,
        default='IMPORTED',
        blank=True,
        verbose_name="Estado de Procesamiento",
        help_text="Estado actual del procesamiento del certificado"
    )
    
    # Archivos en diferentes etapas del procesamiento
    original_pdf = models.FileField(
        upload_to='certificates/original/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="PDF Original",
        help_text="PDF original sin QR"
    )
    
    qr_pdf = models.FileField(
        upload_to='certificates/with_qr/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="PDF con QR",
        help_text="PDF con QR insertado (listo para firma)"
    )
    
    final_pdf = models.FileField(
        upload_to='certificates/final/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="PDF Final Firmado",
        help_text="PDF firmado final (para preview público)"
    )
    
    qr_image = models.FileField(
        upload_to='certificates/qr_codes/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Imagen QR",
        help_text="Imagen del código QR generado"
    )
    
    # Configuración de posicionamiento del QR
    qr_position_x = models.IntegerField(
        default=450,
        verbose_name="Posición X del QR",
        help_text="Posición X del QR en el PDF (píxeles desde la izquierda)"
    )
    
    qr_position_y = models.IntegerField(
        default=50,
        verbose_name="Posición Y del QR",
        help_text="Posición Y del QR en el PDF (píxeles desde arriba)"
    )
    
    qr_size = models.IntegerField(
        default=100,
        verbose_name="Tamaño del QR",
        help_text="Tamaño del código QR en píxeles"
    )
    
    # Metadatos de procesamiento
    processing_errors = models.TextField(
        blank=True,
        verbose_name="Errores de Procesamiento",
        help_text="Errores ocurridos durante el procesamiento"
    )
    
    # Timestamps de procesamiento
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Procesado el",
        help_text="Fecha y hora cuando se procesó el QR"
    )
    
    exported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Exportado el",
        help_text="Fecha y hora cuando se exportó para firma"
    )
    
    final_imported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Importado Final el",
        help_text="Fecha y hora cuando se importó la versión firmada final"
    )

    class Meta:
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['is_external']),
            models.Index(fields=['generated_at']),  # Para queries del dashboard
            models.Index(fields=['is_signed']),  # Para filtros de firmados/sin firmar
            models.Index(fields=['processing_status']),  # Para filtros de procesamiento
            models.Index(fields=['processed_at']),  # Para ordenar por fecha de procesamiento
        ]

    def __str__(self):
        return f"Certificado {self.uuid} - {self.participant.full_name}"
    
    def get_certificate_url(self):
        """Retorna la URL del certificado (externa o interna)"""
        if self.is_external and self.external_url:
            return self.external_url
        elif self.pdf_file:
            return self.pdf_file.url
        return None
    
    # ============================================================================
    # MÉTODOS PARA PROCESAMIENTO DE PDFs CON QR
    # ============================================================================
    
    def get_preview_url(self):
        """Retorna la URL de preview del certificado"""
        return f"/certificado/{self.uuid}/preview/"
    
    def get_qr_preview_data(self):
        """Retorna los datos para el QR de preview"""
        return self.get_preview_url()
    
    def can_process_qr(self):
        """Verifica si el certificado puede procesar QR"""
        return self.processing_status == 'IMPORTED' and self.original_pdf
    
    def can_export_for_signing(self):
        """Verifica si el certificado puede exportarse para firma"""
        return self.processing_status == 'QR_INSERTED' and self.qr_pdf
    
    def can_import_final(self):
        """Verifica si el certificado puede recibir la versión firmada final"""
        return self.processing_status == 'EXPORTED_FOR_SIGNING'
    
    def is_ready_for_preview(self):
        """Verifica si el certificado está listo para preview público"""
        return self.processing_status == 'SIGNED_FINAL' and self.final_pdf
    
    def get_current_pdf(self):
        """Retorna el PDF actual según el estado de procesamiento"""
        if self.processing_status == 'SIGNED_FINAL' and self.final_pdf:
            return self.final_pdf
        elif self.processing_status in ['QR_INSERTED', 'EXPORTED_FOR_SIGNING'] and self.qr_pdf:
            return self.qr_pdf
        elif self.original_pdf:
            return self.original_pdf
        return self.pdf_file  # Fallback al campo original
    
    def get_processing_progress(self):
        """Retorna el progreso de procesamiento como porcentaje"""
        progress_map = {
            'IMPORTED': 20,
            'QR_GENERATED': 40,
            'QR_INSERTED': 60,
            'EXPORTED_FOR_SIGNING': 80,
            'SIGNED_FINAL': 100,
            'ERROR': 0,
        }
        return progress_map.get(self.processing_status, 0)
    
    def mark_processing_error(self, error_message):
        """Marca el certificado con error de procesamiento"""
        self.processing_status = 'ERROR'
        self.processing_errors = error_message
        self.save()



class AuditLog(models.Model):
    """
    Registro de auditoría de acciones del sistema.
    
    Índices de base de datos:
    - timestamp: Para ordenar y filtrar por fecha (usado en dashboard)
    - action_type: Para filtrar por tipo de acción (usado en dashboard para consultas)
    """
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


class QRProcessingConfig(models.Model):
    """
    Configuración global para procesamiento de códigos QR en certificados.
    
    Este modelo almacena la configuración que se usa para generar e insertar
    códigos QR en los certificados PDF durante el flujo de procesamiento.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de Configuración",
        help_text="Nombre identificador de esta configuración"
    )
    
    # ============================================================================
    # CONFIGURACIÓN DE POSICIONAMIENTO DEL QR
    # ============================================================================
    
    default_qr_x = models.IntegerField(
        default=450,
        verbose_name="Posición X por Defecto",
        help_text="Posición X del QR en píxeles desde la izquierda del PDF"
    )
    
    default_qr_y = models.IntegerField(
        default=50,
        verbose_name="Posición Y por Defecto",
        help_text="Posición Y del QR en píxeles desde arriba del PDF"
    )
    
    default_qr_size = models.IntegerField(
        default=100,
        verbose_name="Tamaño por Defecto",
        help_text="Tamaño del código QR en píxeles"
    )
    
    # ============================================================================
    # CONFIGURACIÓN DE CALIDAD DEL QR
    # ============================================================================
    
    QR_ERROR_CORRECTION_CHOICES = [
        ('L', 'Low (7%)'),
        ('M', 'Medium (15%)'),
        ('Q', 'Quartile (25%)'),
        ('H', 'High (30%)'),
    ]
    
    qr_error_correction = models.CharField(
        max_length=1,
        choices=QR_ERROR_CORRECTION_CHOICES,
        default='M',
        verbose_name="Corrección de Errores",
        help_text="Nivel de corrección de errores del código QR"
    )
    
    qr_border = models.IntegerField(
        default=2,
        verbose_name="Borde del QR",
        help_text="Tamaño del borde blanco alrededor del QR (en módulos)"
    )
    
    qr_box_size = models.IntegerField(
        default=10,
        verbose_name="Tamaño de Caja",
        help_text="Tamaño de cada caja/módulo del QR en píxeles"
    )
    
    # ============================================================================
    # CONFIGURACIÓN DE URL BASE
    # ============================================================================
    
    preview_base_url = models.URLField(
        max_length=500,
        default='http://localhost:8000',
        verbose_name="URL Base para Preview",
        help_text="URL base que se usará en los códigos QR para preview de certificados"
    )
    
    # ============================================================================
    # CONFIGURACIÓN DE PROCESAMIENTO
    # ============================================================================
    
    enable_qr_validation = models.BooleanField(
        default=True,
        verbose_name="Habilitar Validación de QR",
        help_text="Validar que el QR generado sea legible antes de insertarlo"
    )
    
    enable_pdf_backup = models.BooleanField(
        default=True,
        verbose_name="Habilitar Respaldo de PDF",
        help_text="Crear respaldo del PDF original antes de insertar el QR"
    )
    
    max_pdf_size_mb = models.IntegerField(
        default=10,
        verbose_name="Tamaño Máximo de PDF (MB)",
        help_text="Tamaño máximo permitido para archivos PDF en megabytes"
    )
    
    # ============================================================================
    # ESTADO Y METADATOS
    # ============================================================================
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Configuración Activa",
        help_text="Indica si esta configuración está activa y debe usarse"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción de esta configuración y su propósito"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_configs_created',
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Configuración de Procesamiento QR"
        verbose_name_plural = "Configuraciones de Procesamiento QR"
        ordering = ['-is_active', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        status = "✓ Activa" if self.is_active else "✗ Inactiva"
        return f"{self.name} ({status})"
    
    def save(self, *args, **kwargs):
        """
        Al guardar, si esta configuración se marca como activa,
        desactivar todas las demás configuraciones.
        """
        if self.is_active:
            QRProcessingConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    def get_qr_preview_url(self, certificate_uuid):
        """
        Construye la URL completa de preview para un certificado.
        
        Args:
            certificate_uuid: UUID del certificado
            
        Returns:
            URL completa de preview
        """
        base = self.preview_base_url.rstrip('/')
        return f"{base}/certificado/{certificate_uuid}/preview/"
    
    def validate_pdf_size(self, file_size_bytes):
        """
        Valida que el tamaño del PDF esté dentro del límite permitido.
        
        Args:
            file_size_bytes: Tamaño del archivo en bytes
            
        Returns:
            bool: True si el tamaño es válido, False en caso contrario
        """
        max_size_bytes = self.max_pdf_size_mb * 1024 * 1024
        return file_size_bytes <= max_size_bytes
    
    def get_qr_settings(self):
        """
        Retorna un diccionario con la configuración del QR para usar en la generación.
        
        Returns:
            dict: Configuración del QR
        """
        return {
            'error_correction': self.qr_error_correction,
            'box_size': self.qr_box_size,
            'border': self.qr_border,
            'size': self.default_qr_size,
        }
    
    def get_position_settings(self):
        """
        Retorna un diccionario con la configuración de posicionamiento.
        
        Returns:
            dict: Configuración de posición
        """
        return {
            'x': self.default_qr_x,
            'y': self.default_qr_y,
            'size': self.default_qr_size,
        }
    
    @classmethod
    def get_active_config(cls):
        """
        Retorna la configuración activa actual.
        Si no existe ninguna, crea una configuración por defecto.
        
        Returns:
            QRProcessingConfig: Configuración activa
        """
        config = cls.objects.filter(is_active=True).first()
        if not config:
            config = cls.objects.create(
                name='Configuración por Defecto',
                description='Configuración creada automáticamente',
                is_active=True
            )
        return config
