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
        parser.add_argument(
            '--update',
            action='store_true',
            help='Actualizar contraseña si el usuario ya existe',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='No solicitar confirmación',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Obtener credenciales
        username = options.get('username') or os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = options.get('email') or os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@drtc.gob.pe')
        password = options.get('password') or os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        update = options.get('update', False)
        noinput = options.get('noinput', False)
        
        # Verificar si el usuario ya existe
        try:
            user = User.objects.get(username=username)
            user_exists = True
        except User.DoesNotExist:
            user_exists = False
        
        if user_exists:
            if update:
                # Actualizar contraseña del usuario existente
                user.set_password(password)
                if email:
                    user.email = email
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Contraseña actualizada para el usuario: {username} ({user.email})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'El usuario "{username}" ya existe. Use --update para actualizar la contraseña.'
                    )
                )
                
                # Listar superusuarios existentes
                superusers = User.objects.filter(is_superuser=True)
                self.stdout.write('\nSuperusuarios encontrados:')
                for su in superusers:
                    self.stdout.write(f'- Usuario: {su.username}, Email: {su.email}, Activo: {su.is_active}')
                self.stdout.write(f'Total: {superusers.count()}')
            return
        
        # Crear nuevo superusuario
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
                    'IMPORTANTE: Cambie la contraseña del superusuario después del primer login en producción'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error al crear superusuario: {str(e)}'
                )
            )
