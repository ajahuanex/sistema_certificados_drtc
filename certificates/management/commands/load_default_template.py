"""
Management command to load the default certificate template into the database.
"""
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from certificates.models import CertificateTemplate
import os


class Command(BaseCommand):
    help = 'Carga la plantilla de certificado por defecto en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la actualización de la plantilla por defecto si ya existe',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Check if default template already exists
        existing_template = CertificateTemplate.objects.filter(is_default=True).first()
        
        if existing_template and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Ya existe una plantilla por defecto: "{existing_template.name}". '
                    'Use --force para actualizarla.'
                )
            )
            return
        
        # Read the HTML template file
        template_path = 'certificates/default_certificate.html'
        
        try:
            # Get the HTML content
            with open(os.path.join('templates', template_path), 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f'No se encontró el archivo de plantilla: templates/{template_path}'
                )
            )
            return
        
        # Extract CSS from HTML (between <style> tags)
        css_start = html_content.find('<style>')
        css_end = html_content.find('</style>')
        css_styles = ''
        
        if css_start != -1 and css_end != -1:
            css_styles = html_content[css_start + 7:css_end].strip()
        
        # Create or update the default template
        if existing_template and force:
            existing_template.name = 'Plantilla Por Defecto DRTC Puno'
            existing_template.html_template = html_content
            existing_template.css_styles = css_styles
            existing_template.field_positions = {
                'participant_name': {'x': 'center', 'y': '80mm'},
                'participant_dni': {'x': 'center', 'y': '95mm'},
                'event_name': {'x': 'center', 'y': '125mm'},
                'event_date': {'x': '240mm', 'y': '180mm'},
                'attendee_type': {'x': 'center', 'y': '110mm'},
                'qr_code': {'x': '30mm', 'y': '165mm'},
                'signature': {'x': 'center', 'y': '175mm'}
            }
            existing_template.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Plantilla por defecto actualizada exitosamente: "{existing_template.name}"'
                )
            )
        else:
            # Ensure no other template is marked as default
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
            
            template = CertificateTemplate.objects.create(
                name='Plantilla Por Defecto DRTC Puno',
                html_template=html_content,
                css_styles=css_styles,
                is_default=True,
                field_positions={
                    'participant_name': {'x': 'center', 'y': '80mm'},
                    'participant_dni': {'x': 'center', 'y': '95mm'},
                    'event_name': {'x': 'center', 'y': '125mm'},
                    'event_date': {'x': '240mm', 'y': '180mm'},
                    'attendee_type': {'x': 'center', 'y': '110mm'},
                    'qr_code': {'x': '30mm', 'y': '165mm'},
                    'signature': {'x': 'center', 'y': '175mm'}
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Plantilla por defecto creada exitosamente: "{template.name}" (ID: {template.id})'
                )
            )
