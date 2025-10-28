"""
Management command to sign certificates for an event.
"""
from django.core.management.base import BaseCommand, CommandError
from certificates.models import Event, Certificate
from certificates.services.digital_signature import DigitalSignatureService


class Command(BaseCommand):
    help = 'Firma digitalmente los certificados de un evento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event-id',
            type=int,
            required=True,
            help='ID del evento cuyos certificados se firmarán',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Firmar todos los certificados, incluso los ya firmados',
        )

    def handle(self, *args, **options):
        event_id = options['event_id']
        sign_all = options.get('all', False)
        
        # Verificar que el evento existe
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise CommandError(f'El evento con ID {event_id} no existe')
        
        self.stdout.write(
            self.style.WARNING(
                f'Firmando certificados para el evento: "{event.name}" ({event.event_date})'
            )
        )
        
        # Obtener certificados del evento
        certificates = Certificate.objects.filter(
            participant__event=event
        ).select_related('participant')
        
        if not certificates.exists():
            self.stdout.write(
                self.style.WARNING(
                    'No hay certificados generados para este evento. '
                    'Primero debe generar los certificados con: '
                    f'python manage.py generate_certificates --event-id {event_id}'
                )
            )
            return
        
        # Filtrar certificados no firmados si no se especifica --all
        if not sign_all:
            unsigned_certificates = certificates.filter(is_signed=False)
            signed_count = certificates.filter(is_signed=True).count()
            
            if signed_count > 0:
                self.stdout.write(
                    f'Certificados ya firmados: {signed_count} (se omitirán)'
                )
            
            certificates = unsigned_certificates
        
        if not certificates.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    'Todos los certificados ya están firmados'
                )
            )
            return
        
        self.stdout.write(
            f'Total de certificados a firmar: {certificates.count()}'
        )
        self.stdout.write('')
        
        # Firmar certificados
        service = DigitalSignatureService()
        
        # Mostrar progreso
        self.stdout.write('Iniciando proceso de firma...')
        self.stdout.write('')
        
        result = service.sign_bulk_certificates(certificates)
        
        # Mostrar resultados
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== RESULTADOS ==='))
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Certificados firmados exitosamente: {result["success_count"]}'
            )
        )
        
        if result['error_count'] > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Errores: {result["error_count"]}'
                )
            )
            
            if result['errors']:
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('Detalles de errores:'))
                for error in result['errors']:
                    self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. Total: {result["success_count"]} éxitos, {result["error_count"]} errores'
            )
        )
        
        # Advertencia sobre servicio de firma
        if result['error_count'] > 0:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    'NOTA: Verifique que el servicio de firma digital esté configurado correctamente '
                    'en las variables de entorno SIGNATURE_SERVICE_URL y SIGNATURE_API_KEY'
                )
            )
