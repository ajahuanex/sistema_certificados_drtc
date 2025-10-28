# Comandos de Management

Esta guía documenta todos los comandos de management personalizados disponibles en el Sistema de Certificados DRTC Puno.

## Tabla de Contenidos

- [Introducción](#introducción)
- [Comandos Personalizados](#comandos-personalizados)
  - [load_default_template](#load_default_template)
  - [generate_certificates](#generate_certificates)
  - [sign_certificates](#sign_certificates)
  - [create_superuser_if_not_exists](#create_superuser_if_not_exists)
- [Comandos Django Estándar](#comandos-django-estándar)
- [Scripts de Automatización](#scripts-de-automatización)
- [Ejemplos de Uso](#ejemplos-de-uso)

## Introducción

Los comandos de management son scripts que se ejecutan desde la línea de comandos para realizar tareas administrativas. Django incluye comandos estándar (como `migrate`, `runserver`, etc.) y el Sistema de Certificados DRTC Puno incluye comandos personalizados para tareas específicas.

### Sintaxis General

```bash
python manage.py <comando> [opciones]
```

### Ayuda

Para ver la ayuda de cualquier comando:

```bash
python manage.py <comando> --help
```

## Comandos Personalizados

### load_default_template

Carga la plantilla de certificado por defecto en la base de datos.

#### Ubicación

`certificates/management/commands/load_default_template.py`

#### Sintaxis

```bash
python manage.py load_default_template [--force]
```

#### Opciones

| Opción | Descripción |
|--------|-------------|
| `--force` | Sobrescribe la plantilla por defecto existente |

#### Descripción

Este comando:

1. Lee el archivo de plantilla HTML: `templates/certificates/default_certificate.html`
2. Crea o actualiza el registro de `CertificateTemplate` en la base de datos
3. Marca la plantilla como predeterminada (`is_default=True`)
4. Configura las posiciones de los campos en el certificado

#### Cuándo Usar

- ✅ Después de la instalación inicial del sistema
- ✅ Después de actualizar el diseño de la plantilla
- ✅ Si se eliminó accidentalmente la plantilla por defecto
- ✅ Para restaurar la plantilla a su estado original

#### Ejemplos

**Cargar plantilla por primera vez:**

```bash
python manage.py load_default_template
```

Salida:
```
Cargando plantilla por defecto...
✅ Plantilla 'Plantilla DRTC Puno' creada exitosamente
```

**Actualizar plantilla existente:**

```bash
python manage.py load_default_template --force
```

Salida:
```
Cargando plantilla por defecto...
⚠️  Ya existe una plantilla por defecto
✅ Plantilla 'Plantilla DRTC Puno' actualizada exitosamente
```

#### Notas

- Si ya existe una plantilla por defecto y no usas `--force`, el comando no hará cambios
- La plantilla se carga desde el archivo HTML, por lo que cualquier modificación al archivo se reflejará al ejecutar el comando con `--force`

---

### generate_certificates

Genera certificados PDF para todos los participantes de un evento específico.

#### Ubicación

`certificates/management/commands/generate_certificates.py`

#### Sintaxis

```bash
python manage.py generate_certificates --event-id <ID> [--regenerate]
```

#### Opciones

| Opción | Requerido | Descripción |
|--------|-----------|-------------|
| `--event-id <ID>` | Sí | ID del evento para el cual generar certificados |
| `--regenerate` | No | Regenera certificados existentes |

#### Descripción

Este comando:

1. Busca el evento por ID
2. Obtiene todos los participantes del evento
3. Para cada participante:
   - Genera un certificado PDF personalizado
   - Crea un código QR único
   - Guarda los archivos en el storage
   - Crea el registro en la base de datos
4. Muestra un resumen de la operación

#### Cuándo Usar

- ✅ Después de importar participantes de un evento
- ✅ Para generar certificados de eventos nuevos
- ✅ Para regenerar certificados después de actualizar la plantilla
- ✅ Para regenerar certificados con datos corregidos

#### Ejemplos

**Generar certificados para un evento:**

```bash
python manage.py generate_certificates --event-id 1
```

Salida:
```
Generando certificados para el evento: Capacitación en Seguridad Vial 2024
Participantes encontrados: 45

Generando certificados...
[████████████████████████████████████████] 45/45

✅ Generación completada:
   - Certificados generados: 45
   - Certificados omitidos (ya existían): 0
   - Errores: 0
   - Tiempo total: 23.5 segundos
```

**Regenerar todos los certificados:**

```bash
python manage.py generate_certificates --event-id 1 --regenerate
```

Salida:
```
Generando certificados para el evento: Capacitación en Seguridad Vial 2024
Participantes encontrados: 45
⚠️  Modo regeneración: Se sobrescribirán certificados existentes

Generando certificados...
[████████████████████████████████████████] 45/45

✅ Generación completada:
   - Certificados generados: 45
   - Certificados regenerados: 45
   - Errores: 0
   - Tiempo total: 24.1 segundos
```

**Error: Evento no encontrado:**

```bash
python manage.py generate_certificates --event-id 999
```

Salida:
```
❌ Error: No se encontró el evento con ID 999
```

#### Notas

- Por defecto, no regenera certificados existentes (los omite)
- Con `--regenerate`, elimina y vuelve a crear los certificados
- Los certificados se guardan en: `media/certificates/YYYY/MM/`
- Los códigos QR se guardan en: `media/qr_codes/YYYY/MM/`

---

### sign_certificates

Envía certificados al servicio de firma digital.

#### Ubicación

`certificates/management/commands/sign_certificates.py`

#### Sintaxis

```bash
python manage.py sign_certificates [--event-id <ID>] [--all] [--retry-failed]
```

#### Opciones

| Opción | Requerido | Descripción |
|--------|-----------|-------------|
| `--event-id <ID>` | Condicional | ID del evento cuyos certificados se firmarán |
| `--all` | Condicional | Firma todos los certificados pendientes (ignora --event-id) |
| `--retry-failed` | No | Reintenta firmar certificados que fallaron anteriormente |

**Nota:** Debes especificar `--event-id` o `--all`, pero no ambos.

#### Descripción

Este comando:

1. Obtiene los certificados a firmar según los filtros
2. Para cada certificado:
   - Verifica que no esté ya firmado
   - Envía el PDF al servicio de firma digital
   - Recibe el PDF firmado
   - Actualiza el certificado en la base de datos
   - Registra la operación en auditoría
3. Muestra un resumen de la operación

#### Cuándo Usar

- ✅ Después de generar certificados nuevos
- ✅ Para firmar certificados pendientes
- ✅ Para reintentar certificados que fallaron
- ✅ En procesos automatizados de firma

#### Ejemplos

**Firmar certificados de un evento:**

```bash
python manage.py sign_certificates --event-id 1
```

Salida:
```
Firmando certificados del evento: Capacitación en Seguridad Vial 2024
Certificados pendientes de firma: 45

Firmando certificados...
[████████████████████████████████████████] 45/45

✅ Firma completada:
   - Certificados firmados exitosamente: 42
   - Certificados que fallaron: 3
   - Certificados omitidos (ya firmados): 0
   - Tiempo total: 156.3 segundos

❌ Errores:
   - Certificado UUID abc123: Timeout al conectar con el servicio
   - Certificado UUID def456: Error 500 del servicio
   - Certificado UUID ghi789: Timeout al conectar con el servicio

💡 Tip: Usa --retry-failed para reintentar los certificados que fallaron
```

**Firmar todos los certificados pendientes:**

```bash
python manage.py sign_certificates --all
```

Salida:
```
Firmando todos los certificados pendientes...
Certificados pendientes de firma: 127

Firmando certificados...
[████████████████████████████████████████] 127/127

✅ Firma completada:
   - Certificados firmados exitosamente: 125
   - Certificados que fallaron: 2
   - Tiempo total: 421.7 segundos
```

**Reintentar certificados que fallaron:**

```bash
python manage.py sign_certificates --event-id 1 --retry-failed
```

Salida:
```
Reintentando firma de certificados del evento: Capacitación en Seguridad Vial 2024
Certificados con errores previos: 3

Firmando certificados...
[████████████████████████████████████████] 3/3

✅ Firma completada:
   - Certificados firmados exitosamente: 3
   - Certificados que fallaron: 0
   - Tiempo total: 12.1 segundos
```

#### Notas

- Requiere configuración correcta del servicio de firma digital
- El proceso puede tomar varios minutos para eventos grandes
- Los certificados ya firmados se omiten automáticamente
- Los errores se registran en `logs/signature.log`
- El sistema reintenta automáticamente 3 veces antes de marcar como fallido

---

### create_superuser_if_not_exists

Crea un superusuario automáticamente si no existe ninguno en el sistema.

#### Ubicación

`certificates/management/commands/create_superuser_if_not_exists.py`

#### Sintaxis

```bash
python manage.py create_superuser_if_not_exists
```

#### Opciones

Este comando no tiene opciones. Lee las credenciales de variables de entorno.

#### Variables de Entorno Requeridas

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
DJANGO_SUPERUSER_PASSWORD=password_seguro_aqui
```

#### Descripción

Este comando:

1. Verifica si ya existe un superusuario en el sistema
2. Si no existe:
   - Lee las credenciales de las variables de entorno
   - Crea un nuevo superusuario
   - Muestra un mensaje de confirmación
3. Si ya existe:
   - No hace nada
   - Muestra un mensaje informativo

#### Cuándo Usar

- ✅ En scripts de deployment automatizado
- ✅ En contenedores Docker
- ✅ En pipelines de CI/CD
- ✅ Para configuración inicial automatizada

#### Ejemplos

**Crear superusuario en deployment:**

```bash
# Configurar variables de entorno
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
export DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32)

# Ejecutar comando
python manage.py create_superuser_if_not_exists
```

Salida (primera ejecución):
```
Verificando superusuarios existentes...
No se encontraron superusuarios
Creando superusuario...
✅ Superusuario 'admin' creado exitosamente
```

Salida (ejecuciones posteriores):
```
Verificando superusuarios existentes...
ℹ️  Ya existe al menos un superusuario en el sistema
No se creó ningún usuario nuevo
```

#### Script de Deployment

```bash
#!/bin/bash
# deploy.sh

set -e

echo "=== Deployment del Sistema de Certificados DRTC ==="

# Configurar variables de entorno
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
export DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32)

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate

# Crear superusuario si no existe
echo "Configurando superusuario..."
python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
echo "Cargando plantilla por defecto..."
python manage.py load_default_template

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Deployment completado"
echo "Usuario: $DJANGO_SUPERUSER_USERNAME"
echo "Contraseña: $DJANGO_SUPERUSER_PASSWORD"
echo "⚠️  Guarda esta contraseña en un lugar seguro"
```

#### Notas

- Solo crea el superusuario si NO existe ninguno
- Las credenciales deben estar en variables de entorno
- Útil para automatización, no para uso manual
- Para crear superusuarios adicionales, usa: `python manage.py createsuperuser`

---

## Comandos Django Estándar

### Gestión de Base de Datos

#### migrate

Aplica migraciones pendientes a la base de datos.

```bash
python manage.py migrate
```

Opciones útiles:
```bash
# Ver migraciones sin aplicarlas
python manage.py migrate --plan

# Aplicar migraciones de una app específica
python manage.py migrate certificates

# Revertir a una migración específica
python manage.py migrate certificates 0003
```

#### makemigrations

Crea nuevas migraciones basadas en cambios en los modelos.

```bash
python manage.py makemigrations
```

Opciones útiles:
```bash
# Crear migraciones para una app específica
python manage.py makemigrations certificates

# Ver SQL que se ejecutará
python manage.py sqlmigrate certificates 0001

# Verificar problemas sin crear migraciones
python manage.py makemigrations --check
```

#### showmigrations

Muestra todas las migraciones y su estado.

```bash
python manage.py showmigrations
```

Salida:
```
certificates
 [X] 0001_initial
 [X] 0002_add_audit_log
 [X] 0003_add_certificate_template
 [ ] 0004_add_signature_fields
```

#### dbshell

Abre una shell de la base de datos.

```bash
python manage.py dbshell
```

### Gestión de Usuarios

#### createsuperuser

Crea un superusuario de forma interactiva.

```bash
python manage.py createsuperuser
```

Interacción:
```
Username: admin
Email address: admin@drtcpuno.gob.pe
Password: 
Password (again): 
Superuser created successfully.
```

#### changepassword

Cambia la contraseña de un usuario.

```bash
python manage.py changepassword admin
```

### Gestión de Archivos Estáticos

#### collectstatic

Recolecta archivos estáticos en STATIC_ROOT.

```bash
python manage.py collectstatic
```

Opciones útiles:
```bash
# Sin confirmación (para scripts)
python manage.py collectstatic --noinput

# Limpiar archivos antiguos
python manage.py collectstatic --clear

# Modo dry-run (ver qué se haría)
python manage.py collectstatic --dry-run
```

### Servidor de Desarrollo

#### runserver

Inicia el servidor de desarrollo.

```bash
python manage.py runserver
```

Opciones útiles:
```bash
# Puerto personalizado
python manage.py runserver 8080

# Escuchar en todas las interfaces
python manage.py runserver 0.0.0.0:8000

# Sin auto-reload
python manage.py runserver --noreload
```

### Utilidades

#### shell

Abre una shell de Python con Django configurado.

```bash
python manage.py shell
```

Ejemplo de uso:
```python
from certificates.models import Event, Participant, Certificate

# Ver estadísticas
print(f"Eventos: {Event.objects.count()}")
print(f"Participantes: {Participant.objects.count()}")
print(f"Certificados: {Certificate.objects.count()}")
print(f"Certificados firmados: {Certificate.objects.filter(is_signed=True).count()}")
```

#### check

Verifica problemas en el proyecto.

```bash
python manage.py check
```

Opciones útiles:
```bash
# Verificar configuración de producción
python manage.py check --deploy

# Verificar solo una app
python manage.py check certificates

# Nivel de severidad
python manage.py check --tag security
```

#### test

Ejecuta tests.

```bash
python manage.py test
```

Opciones útiles:
```bash
# Tests de una app específica
python manage.py test certificates

# Test específico
python manage.py test certificates.tests.test_models.ParticipantModelTest

# Con cobertura
coverage run --source='.' manage.py test
coverage report

# Modo verbose
python manage.py test --verbosity=2

# Mantener base de datos de test
python manage.py test --keepdb
```

## Scripts de Automatización

### Script de Backup

```bash
#!/bin/bash
# backup.sh - Backup automático de base de datos y archivos

BACKUP_DIR="/var/backups/certificados"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
echo "Respaldando base de datos..."
pg_dump -U certificados_user certificados_drtc | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup de archivos media
echo "Respaldando archivos media..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /var/www/certificados media/

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup completado: $DATE"
```

### Script de Deployment

```bash
#!/bin/bash
# deploy.sh - Script de deployment completo

set -e

echo "=== Deployment del Sistema de Certificados DRTC ==="

# Activar entorno virtual
source venv/bin/activate

# Actualizar código
echo "Actualizando código..."
git pull origin main

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate

# Crear superusuario si no existe
echo "Configurando superusuario..."
python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
echo "Cargando plantilla por defecto..."
python manage.py load_default_template --force

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar servicio
echo "Reiniciando servicio..."
sudo systemctl restart certificados

echo "✅ Deployment completado"
```

### Script de Generación Masiva

```bash
#!/bin/bash
# generate_all_certificates.sh - Genera certificados para todos los eventos

echo "=== Generación Masiva de Certificados ==="

# Obtener IDs de eventos sin certificados
EVENT_IDS=$(python manage.py shell -c "
from certificates.models import Event, Certificate
events = Event.objects.all()
for event in events:
    cert_count = Certificate.objects.filter(participant__event=event).count()
    participant_count = event.participant_set.count()
    if cert_count < participant_count:
        print(event.id)
")

# Generar certificados para cada evento
for EVENT_ID in $EVENT_IDS; do
    echo "Generando certificados para evento $EVENT_ID..."
    python manage.py generate_certificates --event-id $EVENT_ID
done

echo "✅ Generación masiva completada"
```

### Script de Firma Automática

```bash
#!/bin/bash
# auto_sign.sh - Firma automática de certificados pendientes

echo "=== Firma Automática de Certificados ==="

# Firmar todos los certificados pendientes
python manage.py sign_certificates --all

# Si hay errores, reintentar
FAILED_COUNT=$(python manage.py shell -c "
from certificates.models import Certificate
print(Certificate.objects.filter(is_signed=False).count())
")

if [ $FAILED_COUNT -gt 0 ]; then
    echo "⚠️  Hay $FAILED_COUNT certificados pendientes. Reintentando..."
    sleep 60  # Esperar 1 minuto
    python manage.py sign_certificates --all --retry-failed
fi

echo "✅ Firma automática completada"
```

### Cron Jobs

Agregar a crontab para automatización:

```bash
# Editar crontab
crontab -e

# Agregar jobs
# Backup diario a las 2 AM
0 2 * * * /var/www/certificados/backup.sh

# Firma automática cada hora
0 * * * * /var/www/certificados/auto_sign.sh

# Generación de certificados pendientes cada 6 horas
0 */6 * * * /var/www/certificados/generate_all_certificates.sh
```

## Ejemplos de Uso

### Flujo Completo: Nuevo Evento

```bash
# 1. Importar participantes (desde el panel web)
# ...

# 2. Generar certificados
python manage.py generate_certificates --event-id 5

# 3. Firmar certificados
python manage.py sign_certificates --event-id 5

# 4. Verificar resultados
python manage.py shell -c "
from certificates.models import Event, Certificate
event = Event.objects.get(id=5)
total = event.participant_set.count()
generated = Certificate.objects.filter(participant__event=event).count()
signed = Certificate.objects.filter(participant__event=event, is_signed=True).count()
print(f'Total participantes: {total}')
print(f'Certificados generados: {generated}')
print(f'Certificados firmados: {signed}')
"
```

### Regenerar Certificados con Nueva Plantilla

```bash
# 1. Actualizar plantilla
python manage.py load_default_template --force

# 2. Regenerar certificados de un evento
python manage.py generate_certificates --event-id 3 --regenerate

# 3. Firmar nuevamente
python manage.py sign_certificates --event-id 3
```

### Mantenimiento Semanal

```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== Mantenimiento Semanal ==="

# Backup
echo "1. Realizando backup..."
./backup.sh

# Verificar certificados pendientes
echo "2. Verificando certificados pendientes..."
python manage.py shell -c "
from certificates.models import Certificate, Participant
total_participants = Participant.objects.count()
total_certificates = Certificate.objects.count()
signed_certificates = Certificate.objects.filter(is_signed=True).count()
print(f'Participantes: {total_participants}')
print(f'Certificados: {total_certificates}')
print(f'Firmados: {signed_certificates}')
print(f'Pendientes de generar: {total_participants - total_certificates}')
print(f'Pendientes de firmar: {total_certificates - signed_certificates}')
"

# Generar certificados pendientes
echo "3. Generando certificados pendientes..."
./generate_all_certificates.sh

# Firmar certificados pendientes
echo "4. Firmando certificados pendientes..."
./auto_sign.sh

# Limpiar logs antiguos
echo "5. Limpiando logs antiguos..."
find logs/ -name "*.log" -mtime +90 -delete

echo "✅ Mantenimiento completado"
```

## Troubleshooting

### Comando no encontrado

**Error:**
```
Unknown command: 'generate_certificates'
```

**Solución:**
```bash
# Verificar que el comando existe
ls certificates/management/commands/

# Verificar que __init__.py existe en cada directorio
ls certificates/management/__init__.py
ls certificates/management/commands/__init__.py

# Reiniciar shell de Django
python manage.py shell
```

### Error de permisos

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solución:**
```bash
# Verificar permisos de archivos
ls -la certificates/management/commands/

# Dar permisos de ejecución
chmod +x certificates/management/commands/*.py

# Verificar permisos de directorios media y logs
chmod 755 media/ logs/
```

### Error de importación

**Error:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Solución:**
```bash
# Verificar instalación de dependencias
pip install -r requirements.txt

# Verificar PYTHONPATH
echo $PYTHONPATH

# Ejecutar desde el directorio raíz del proyecto
cd /path/to/proyecto
python manage.py <comando>
```

---

**Última actualización:** 28 de octubre de 2024
