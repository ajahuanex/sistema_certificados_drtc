#!/usr/bin/env python
"""Script para resetear la contraseña del admin"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Actualizar o crear admin
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.email = 'admin@drtc.gob.pe'
    admin.is_superuser = True
    admin.is_staff = True
    admin.is_active = True
    admin.save()
    print('✓ Contraseña actualizada para admin')
    print(f'  Usuario: admin')
    print(f'  Email: {admin.email}')
    print(f'  Contraseña: admin123')
except User.DoesNotExist:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@drtc.gob.pe',
        password='admin123'
    )
    print('✓ Usuario admin creado')
    print(f'  Usuario: admin')
    print(f'  Email: admin@drtc.gob.pe')
    print(f'  Contraseña: admin123')

print('\n✓ Ahora puedes acceder con admin/admin123')
