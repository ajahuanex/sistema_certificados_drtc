"""
Comando de gestión para migrar plantillas HTML al formato visual.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from certificates.models import CertificateTemplate
from certificates.services.template_migration import TemplateMigrationService


class Command(BaseCommand):
    help = 'Migra plantillas HTML existentes al formato visual del editor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template-id',
            type=int,
            help='ID de una plantilla específica a migrar'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Migrar todas las plantillas que no tienen elementos visuales'
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Solo mostrar qué se migraría sin hacer cambios'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar migración incluso si la plantilla ya tiene elementos'
        )
        parser.add_argument(
            '--no-preserve',
            action='store_true',
            help='No preservar el HTML original como comentario'
        )

    def handle(self, *args, **options):
        service = TemplateMigrationService()
        
        # Migración de plantilla específica
        if options['template_id']:
            return self._migrate_single_template(service, options)
        
        # Migración de todas las plantillas
        elif options['all']:
            return self._migrate_all_templates(service, options)
        
        # Mostrar ayuda si no se especifican opciones
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Debe especificar --template-id <ID> o --all para migrar plantillas'
                )
            )
            self.stdout.write('')
            self.stdout.write('Ejemplos:')
            self.stdout.write('  python manage.py migrate_templates --template-id 1 --preview')
            self.stdout.write('  python manage.py migrate_templates --all')
            self.stdout.write('  python manage.py migrate_templates --template-id 1 --no-preserve')

    def _migrate_single_template(self, service, options):
        """Migra una plantilla específica"""
        template_id = options['template_id']
        
        try:
            template = CertificateTemplate.objects.get(id=template_id)
        except CertificateTemplate.DoesNotExist:
            raise CommandError(f'Plantilla con ID {template_id} no encontrada')
        
        self.stdout.write(f'Procesando plantilla: {template.name} (ID: {template_id})')
        
        # Preview mode
        if options['preview']:
            result = service.preview_migration(template_id)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Preview de migración para "{template.name}":')
                )
                self.stdout.write(f'  - Total de elementos: {result["total_elements"]}')
                self.stdout.write(f'  - Variables: {result["elements_by_type"]["variables"]}')
                self.stdout.write(f'  - Texto: {result["elements_by_type"]["text"]}')
                self.stdout.write(f'  - Imágenes: {result["elements_by_type"]["images"]}')
                
                if result['elements_preview']:
                    self.stdout.write('  - Elementos a crear:')
                    for elem in result['elements_preview']:
                        self.stdout.write(f'    * {elem["type"]}: {elem["name"]}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error en preview: {result["error"]}')
                )
            return
        
        # Verificar si ya tiene elementos
        if template.elements.exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ La plantilla "{template.name}" ya tiene {template.elements.count()} elementos visuales'
                )
            )
            self.stdout.write('Use --force para migrar de todas formas')
            return
        
        # Realizar migración
        preserve_original = not options['no_preserve']
        result = service.migrate_template(template_id, preserve_original)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Plantilla "{template.name}" migrada exitosamente'
                )
            )
            self.stdout.write(f'  - Elementos creados: {result["elements_created"]}')
            
            if result.get('elements'):
                for elem in result['elements']:
                    self.stdout.write(
                        f'    * {elem["type"]}: {elem["name"]} en {elem["position"]} ({elem["size"]})'
                    )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Error migrando plantilla: {result["error"]}')
            )

    def _migrate_all_templates(self, service, options):
        """Migra todas las plantillas"""
        
        # Preview mode
        if options['preview']:
            templates = CertificateTemplate.objects.all()
            if not options['force']:
                templates = templates.filter(elements__isnull=True).distinct()
            
            self.stdout.write(f'Preview de migración masiva para {templates.count()} plantillas:')
            self.stdout.write('')
            
            for template in templates:
                result = service.preview_migration(template.id)
                if result['success']:
                    self.stdout.write(
                        f'✓ {template.name} (ID: {template.id}): {result["total_elements"]} elementos'
                    )
                else:
                    self.stdout.write(
                        f'✗ {template.name} (ID: {template.id}): {result["error"]}'
                    )
            return
        
        # Confirmar migración masiva
        templates = CertificateTemplate.objects.all()
        if not options['force']:
            templates = templates.filter(elements__isnull=True).distinct()
        
        if not templates.exists():
            self.stdout.write(
                self.style.WARNING('No hay plantillas para migrar')
            )
            return
        
        self.stdout.write(f'Se migrarán {templates.count()} plantillas.')
        
        # Pedir confirmación en modo interactivo
        if not options.get('verbosity', 1) == 0:  # No en modo silencioso
            confirm = input('¿Continuar? (s/N): ')
            if confirm.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                self.stdout.write('Migración cancelada')
                return
        
        # Realizar migración masiva
        exclude_with_elements = not options['force']
        preserve_original = not options['no_preserve']
        
        self.stdout.write('Iniciando migración masiva...')
        
        results = service.migrate_all_templates(exclude_with_elements)
        
        # Mostrar resultados
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Migración completada: {results["migrated_successfully"]} éxitos, '
                f'{results["migration_errors"]} errores'
            )
        )
        
        # Mostrar detalles de éxitos
        if results['migrated_successfully'] > 0:
            self.stdout.write('')
            self.stdout.write('Plantillas migradas exitosamente:')
            for result in results['results']:
                if result['success']:
                    self.stdout.write(
                        f'  ✓ {result["template_name"]} (ID: {result["template_id"]}): '
                        f'{result["elements_created"]} elementos'
                    )
        
        # Mostrar errores
        if results['migration_errors'] > 0:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Errores encontrados:'))
            for error in results['errors']:
                self.stdout.write(
                    f'  ✗ {error["template_name"]} (ID: {error["template_id"]}): {error["error"]}'
                )
        
        self.stdout.write('')
        self.stdout.write(
            f'Total procesado: {results["total_templates"]} plantillas'
        )