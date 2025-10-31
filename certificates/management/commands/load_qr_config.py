"""
Comando de gestión para cargar configuración inicial de procesamiento QR.
"""
from django.core.management.base import BaseCommand
from certificates.models import QRProcessingConfig


class Command(BaseCommand):
    help = 'Carga la configuración inicial para procesamiento de QR en certificados'

    def handle(self, *args, **options):
        """Crea la configuración por defecto si no existe"""
        
        # Verificar si ya existe una configuración
        if QRProcessingConfig.objects.exists():
            self.stdout.write(
                self.style.WARNING('Ya existe una configuración de QR. No se creará una nueva.')
            )
            
            # Mostrar configuración activa
            active_config = QRProcessingConfig.objects.filter(is_active=True).first()
            if active_config:
                self.stdout.write(
                    self.style.SUCCESS(f'Configuración activa: {active_config.name}')
                )
            return
        
        # Crear configuración por defecto
        config = QRProcessingConfig.objects.create(
            name='Configuración Estándar',
            description='Configuración por defecto para procesamiento de certificados con QR',
            default_qr_x=450,
            default_qr_y=50,
            default_qr_size=100,
            qr_error_correction='M',
            qr_border=2,
            qr_box_size=10,
            preview_base_url='http://localhost:8000',
            enable_qr_validation=True,
            enable_pdf_backup=True,
            max_pdf_size_mb=10,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Configuración creada exitosamente: {config.name}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'  - Posición QR: ({config.default_qr_x}, {config.default_qr_y})')
        )
        self.stdout.write(
            self.style.SUCCESS(f'  - Tamaño QR: {config.default_qr_size}px')
        )
        self.stdout.write(
            self.style.SUCCESS(f'  - URL Base: {config.preview_base_url}')
        )
