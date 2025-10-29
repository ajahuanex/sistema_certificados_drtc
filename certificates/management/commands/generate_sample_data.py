"""Comando para generar datos de muestra para el dashboard"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from certificates.models import Event, Participant, Certificate, CertificateTemplate, AuditLog
from certificates.services.certificate_generator import CertificateGeneratorService
from certificates.services.qr_service import QRCodeService


class Command(BaseCommand):
    """Genera datos de muestra para demostrar el dashboard"""
    
    help = 'Genera datos de muestra para el dashboard de estadísticas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--events',
            type=int,
            default=10,
            help='Número de eventos a crear (default: 10)'
        )
        
        parser.add_argument(
            '--participants-per-event',
            type=int,
            default=15,
            help='Número promedio de participantes por evento (default: 15)'
        )
        
        parser.add_argument(
            '--months-back',
            type=int,
            default=12,
            help='Meses hacia atrás para distribuir eventos (default: 12)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar datos existentes antes de generar nuevos'
        )
    
    def handle(self, *args, **options):
        """Ejecuta el comando"""
        if options['clear']:
            self.stdout.write('🗑️  Limpiando datos existentes...')
            self.clear_existing_data()
        
        self.stdout.write('🎯 Generando datos de muestra...')
        
        # Crear plantilla si no existe
        template = self.ensure_default_template()
        
        # Generar eventos
        events = self.generate_events(
            count=options['events'],
            months_back=options['months_back'],
            template=template
        )
        
        # Generar participantes
        total_participants = self.generate_participants(
            events=events,
            avg_per_event=options['participants_per_event']
        )
        
        # Generar certificados
        total_certificates = self.generate_certificates(events)
        
        # Generar actividad de auditoría
        self.generate_audit_logs(total_participants)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Datos generados exitosamente:\n'
                f'   📅 Eventos: {len(events)}\n'
                f'   👥 Participantes: {total_participants}\n'
                f'   📜 Certificados: {total_certificates}\n'
                f'   📊 Dashboard listo para usar!'
            )
        )
    
    def clear_existing_data(self):
        """Limpia datos existentes"""
        Certificate.objects.all().delete()
        Participant.objects.all().delete()
        Event.objects.all().delete()
        AuditLog.objects.all().delete()
        
        self.stdout.write('   ✓ Datos limpiados')
    
    def ensure_default_template(self):
        """Asegura que existe una plantilla por defecto"""
        template, created = CertificateTemplate.objects.get_or_create(
            is_default=True,
            defaults={
                'name': 'Plantilla Por Defecto DRTC Puno',
                'html_template': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .certificate { border: 3px solid #007cba; padding: 40px; }
                        .title { font-size: 36px; color: #007cba; margin-bottom: 30px; }
                        .participant { font-size: 24px; font-weight: bold; margin: 20px 0; }
                        .event { font-size: 18px; margin: 15px 0; }
                    </style>
                </head>
                <body>
                    <div class="certificate">
                        <div class="title">CERTIFICADO</div>
                        <p>Se otorga el presente certificado a:</p>
                        <div class="participant">{{ full_name }}</div>
                        <p>DNI: {{ dni }}</p>
                        <p>Por su participación como {{ attendee_type }} en:</p>
                        <div class="event">{{ event_name }}</div>
                        <p>Realizado el {{ event_date }}</p>
                    </div>
                </body>
                </html>
                ''',
                'css_styles': '',
                'field_positions': {
                    'participant_name': {'x': 'center', 'y': '120mm'},
                    'participant_dni': {'x': 'center', 'y': '140mm'},
                    'event_name': {'x': 'center', 'y': '180mm'},
                    'event_date': {'x': 'center', 'y': '200mm'},
                    'attendee_type': {'x': 'center', 'y': '160mm'},
                    'qr_code': {'x': '20mm', 'y': '20mm'},
                    'signature': {'x': 'center', 'y': '220mm'}
                }
            }
        )
        
        if created:
            self.stdout.write('   ✓ Plantilla por defecto creada')
        
        return template
    
    def generate_events(self, count, months_back, template):
        """Genera eventos de muestra"""
        events = []
        
        event_names = [
            "Capacitación en Seguridad Vial",
            "Taller de Transporte Público",
            "Seminario de Normativas de Tránsito",
            "Curso de Licencias de Conducir",
            "Workshop de Tecnología Vehicular",
            "Conferencia de Movilidad Urbana",
            "Capacitación en Primeros Auxilios",
            "Taller de Educación Vial",
            "Seminario de Gestión de Transporte",
            "Curso de Inspección Vehicular",
            "Capacitación en Señalización Vial",
            "Taller de Medio Ambiente y Transporte",
            "Seminario de Logística de Transporte",
            "Curso de Atención al Usuario",
            "Workshop de Innovación en Transporte"
        ]
        
        for i in range(count):
            # Fecha aleatoria en los últimos meses
            days_back = random.randint(0, months_back * 30)
            event_date = timezone.now().date() - timedelta(days=days_back)
            
            # Nombre aleatorio
            event_name = random.choice(event_names)
            if Event.objects.filter(name=event_name, event_date=event_date).exists():
                event_name = f"{event_name} {i+1}"
            
            event = Event.objects.create(
                name=event_name,
                event_date=event_date,
                description=f"Descripción del evento {event_name}",
                template=template
            )
            
            events.append(event)
        
        self.stdout.write(f'   ✓ {count} eventos creados')
        return events
    
    def generate_participants(self, events, avg_per_event):
        """Genera participantes para los eventos"""
        first_names = [
            "Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "José", "Rosa",
            "Miguel", "Elena", "Pedro", "Isabel", "Antonio", "Patricia", "Francisco",
            "Laura", "Manuel", "Sofía", "Jesús", "Lucía", "Alejandro", "Marta",
            "David", "Paula", "Daniel", "Cristina", "Rafael", "Beatriz", "Javier"
        ]
        
        last_names = [
            "García", "Rodríguez", "González", "Fernández", "López", "Martínez",
            "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández",
            "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
            "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez",
            "Serrano", "Blanco", "Suárez", "Molina", "Morales", "Ortega", "Delgado"
        ]
        
        attendee_types = ['ASISTENTE', 'PONENTE', 'ORGANIZADOR']
        attendee_weights = [0.8, 0.15, 0.05]  # 80% asistentes, 15% ponentes, 5% organizadores
        
        total_participants = 0
        
        for event in events:
            # Número aleatorio de participantes (variación del promedio)
            num_participants = random.randint(
                max(1, avg_per_event - 5),
                avg_per_event + 10
            )
            
            for i in range(num_participants):
                # Generar DNI único
                dni = f"{random.randint(10000000, 99999999)}"
                while Participant.objects.filter(dni=dni, event=event).exists():
                    dni = f"{random.randint(10000000, 99999999)}"
                
                # Nombre aleatorio
                first_name = random.choice(first_names)
                last_name1 = random.choice(last_names)
                last_name2 = random.choice(last_names)
                full_name = f"{first_name} {last_name1} {last_name2}"
                
                # Tipo de asistente con pesos
                attendee_type = random.choices(attendee_types, weights=attendee_weights)[0]
                
                Participant.objects.create(
                    dni=dni,
                    full_name=full_name,
                    event=event,
                    attendee_type=attendee_type
                )
                
                total_participants += 1
        
        self.stdout.write(f'   ✓ {total_participants} participantes creados')
        return total_participants
    
    def generate_certificates(self, events):
        """Genera certificados para algunos participantes"""
        total_certificates = 0
        qr_service = QRCodeService()
        
        for event in events:
            participants = list(event.participants.all())
            
            # Generar certificados para 60-90% de los participantes
            cert_percentage = random.uniform(0.6, 0.9)
            num_certificates = int(len(participants) * cert_percentage)
            
            # Seleccionar participantes aleatoriamente
            selected_participants = random.sample(participants, num_certificates)
            
            for participant in selected_participants:
                # Crear certificado básico
                certificate = Certificate.objects.create(
                    participant=participant,
                    pdf_file=f"certificates/sample_{participant.dni}_{event.id}.pdf",
                    qr_code=f"qr_codes/sample_{participant.dni}_{event.id}.png",
                    verification_url=f"http://localhost:8000/verificar/{participant.dni}/"
                )
                
                # 70% de probabilidad de estar firmado
                if random.random() < 0.7:
                    certificate.is_signed = True
                    certificate.signed_at = timezone.now() - timedelta(
                        days=random.randint(0, 30)
                    )
                    certificate.save()
                
                total_certificates += 1
        
        self.stdout.write(f'   ✓ {total_certificates} certificados creados')
        return total_certificates
    
    def generate_audit_logs(self, total_participants):
        """Genera logs de auditoría de muestra"""
        actions = [
            ('IMPORT', 'Importación de participantes desde Excel'),
            ('GENERATE', 'Generación de certificado'),
            ('SIGN', 'Firma digital de certificado'),
            ('QUERY', 'Consulta de certificado por DNI'),
            ('VERIFY', 'Verificación de certificado por QR')
        ]
        
        # Generar logs distribuidos en el tiempo
        num_logs = min(500, total_participants * 3)  # Máximo 500 logs
        
        for i in range(num_logs):
            action_type, description = random.choice(actions)
            
            # Timestamp aleatorio en los últimos 90 días
            days_back = random.randint(0, 90)
            hours_back = random.randint(0, 23)
            timestamp = timezone.now() - timedelta(days=days_back, hours=hours_back)
            
            # IP aleatoria
            ip_address = f"{random.randint(192, 203)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            AuditLog.objects.create(
                action_type=action_type,
                description=f"{description} - Muestra {i+1}",
                timestamp=timestamp,
                ip_address=ip_address,
                metadata={
                    'sample_data': True,
                    'generated_by': 'generate_sample_data command'
                }
            )
        
        self.stdout.write(f'   ✓ {num_logs} logs de auditoría creados')