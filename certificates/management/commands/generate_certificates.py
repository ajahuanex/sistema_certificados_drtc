"""
Management command to generate certificates for an event.
"""
from django.core.management.base import BaseCommand, CommandError
from certificates.models import Event
from certificates.services.certificate_generator import CertificateGeneratorService


class Command(BaseCommand):
    help = 'Genera certificados para todos los participantes de un evento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event-id',
            type=int,
            required=True,
            help='ID del evento para el cual generar certificados',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerar certificados incluso si ya existen',
        )

    def handle(self, *args, **options):
        event_id = options['event_id']
        force = options.get('force', False)
        
        # Verificar que el evento existe
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise CommandError(f'El evento con ID {event_id} no existe')
        
        self.stdout.write(
            self.style.WARNING(
                f'Generando certificados para el evento: "{event.name}" ({event.event_date})'
            )
        )
        
        # Obtener participantes
        participants = event.participants.all()
        
        if not participants.exists():
            self.stdout.write(
                self.style.WARNING(
                    'No hay participantes registrados para este evento'
                )
            )
            return
        
        self.stdout.write(
            f'Total de participantes: {participants.count()}'
        )
        
        # Generar certificados
        service = CertificateGeneratorService()
        
        if force:
            # Si force está activado, eliminar certificados existentes
            from certificates.models import Certificate
            existing_count = Certificate.objects.filter(
                participant__event=event
            ).count()
            
            if existing_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'Eliminando {existing_count} certificados existentes...'
                    )
                )
                Certificate.objects.filter(participant__event=event).delete()
        
        # Generar certificados masivamente
        result = service.generate_bulk_certificates(event)
        
        # Mostrar resultados
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== RESULTADOS ==='))
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Certificados generados exitosamente: {result["success_count"]}'
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
