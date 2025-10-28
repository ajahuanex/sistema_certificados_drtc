"""
Management command to create a superuser if none exists.
Useful for automated deployments.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Crea un superusuario si no existe ninguno (útil para deployment)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='Nombre de usuario del superusuario (por defecto: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default=None,
            help='Email del superusuario (por defecto: admin@example.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Contraseña del superusuario (por defecto: lee de DJANGO_SUPERUSER_PASSWORD)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Verificar si ya existe algún superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(
                    'Ya existe al menos un superusuario. No se creará uno nuevo.'
                )
            )
            return
        
        # Obtener credenciales
        username = options.get('username') or os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = options.get('email') or os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = options.get('password') or os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        # Validar que se proporcionó una contraseña
        if not password:
            self.stdout.write(
                self.style.ERROR(
                    'Debe proporcionar una contraseña mediante --password o la variable '
                    'de entorno DJANGO_SUPERUSER_PASSWORD'
                )
            )
            return
        
        # Crear superusuario
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Superusuario creado exitosamente: {username} ({email})'
                )
            )
            
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    'IMPORTANTE: Cambie la contraseña del superusuario después del primer login'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error al crear superusuario: {str(e)}'
                )
            )
