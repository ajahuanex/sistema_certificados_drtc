# Task 16: Comandos de Management - Resumen de Implementación

## Objetivo
Crear comandos de management de Django para facilitar operaciones administrativas comunes del sistema de certificados.

## Comandos Implementados

### 1. load_default_template
**Archivo**: `certificates/management/commands/load_default_template.py`

**Propósito**: Carga la plantilla de certificado por defecto en la base de datos.

**Uso**:
```bash
# Crear plantilla por defecto
python manage.py load_default_template

# Forzar actualización de plantilla existente
python manage.py load_default_template --force
```

**Características**:
- ✅ Lee el archivo HTML de la plantilla desde `templates/certificates/default_certificate.html`
- ✅ Extrae CSS automáticamente del HTML
- ✅ Configura posiciones de campos (nombre, DNI, evento, fecha, QR, etc.)
- ✅ Previene sobrescritura accidental sin flag `--force`
- ✅ Asegura que solo una plantilla esté marcada como predeterminada
- ✅ Mensajes informativos de éxito/error

**Opciones**:
- `--force`: Actualiza la plantilla por defecto si ya existe

---

### 2. generate_certificates
**Archivo**: `certificates/management/commands/generate_certificates.py`

**Propósito**: Genera certificados PDF para todos los participantes de un evento.

**Uso**:
```bash
# Generar certificados para un evento
python manage.py generate_certificates --event-id 1

# Regenerar certificados (elimina existentes)
python manage.py generate_certificates --event-id 1 --force
```

**Características**:
- ✅ Valida que el evento existe
- ✅ Verifica que hay participantes registrados
- ✅ Genera certificados con QR único para cada participante
- ✅ Muestra progreso y estadísticas detalladas
- ✅ Maneja errores individualmente sin detener el proceso
- ✅ Opción `--force` para regenerar certificados existentes
- ✅ Reporte final con éxitos y errores

**Opciones**:
- `--event-id` (requerido): ID del evento
- `--force`: Elimina y regenera certificados existentes

**Salida de ejemplo**:
```
Generando certificados para el evento: "Capacitación Django" (2024-01-15)
Total de participantes: 50

=== RESULTADOS ===
✓ Certificados generados exitosamente: 50

Proceso completado. Total: 50 éxitos, 0 errores
```

---

### 3. sign_certificates
**Archivo**: `certificates/management/commands/sign_certificates.py`

**Propósito**: Firma digitalmente los certificados de un evento usando el servicio externo.

**Uso**:
```bash
# Firmar certificados no firmados de un evento
python manage.py sign_certificates --event-id 1

# Firmar todos los certificados (incluso ya firmados)
python manage.py sign_certificates --event-id 1 --all
```

**Características**:
- ✅ Valida que el evento existe
- ✅ Verifica que hay certificados generados
- ✅ Filtra automáticamente certificados ya firmados (sin `--all`)
- ✅ Usa el servicio de firma digital con reintentos automáticos
- ✅ Muestra progreso durante el proceso
- ✅ Maneja errores de conexión gracefully
- ✅ Reporte detallado de éxitos y errores
- ✅ Advertencia sobre configuración del servicio de firma

**Opciones**:
- `--event-id` (requerido): ID del evento
- `--all`: Intenta firmar todos los certificados, incluso los ya firmados

**Salida de ejemplo**:
```
Firmando certificados para el evento: "Capacitación Django" (2024-01-15)
Certificados ya firmados: 10 (se omitirán)
Total de certificados a firmar: 40

Iniciando proceso de firma...

=== RESULTADOS ===
✓ Certificados firmados exitosamente: 40

Proceso completado. Total: 40 éxitos, 0 errores
```

**Nota**: Si hay errores, muestra advertencia sobre verificar las variables de entorno `SIGNATURE_SERVICE_URL` y `SIGNATURE_API_KEY`.

---

### 4. create_superuser_if_not_exists
**Archivo**: `certificates/management/commands/create_superuser_if_not_exists.py`

**Propósito**: Crea un superusuario si no existe ninguno (útil para deployment automatizado).

**Uso**:
```bash
# Usando argumentos
python manage.py create_superuser_if_not_exists \
    --username admin \
    --email admin@example.com \
    --password secretpass123

# Usando variables de entorno
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@example.com
export DJANGO_SUPERUSER_PASSWORD=secretpass123
python manage.py create_superuser_if_not_exists

# Usando valores por defecto (requiere password)
python manage.py create_superuser_if_not_exists --password secretpass123
```

**Características**:
- ✅ Verifica si ya existe un superusuario (no crea duplicados)
- ✅ Soporta argumentos de línea de comandos
- ✅ Soporta variables de entorno (ideal para CI/CD)
- ✅ Valores por defecto: username=admin, email=admin@example.com
- ✅ Requiere contraseña obligatoriamente (seguridad)
- ✅ Advertencia para cambiar contraseña después del primer login
- ✅ Manejo de errores con mensajes claros

**Opciones**:
- `--username`: Nombre de usuario (default: admin o DJANGO_SUPERUSER_USERNAME)
- `--email`: Email (default: admin@example.com o DJANGO_SUPERUSER_EMAIL)
- `--password`: Contraseña (requerido, o DJANGO_SUPERUSER_PASSWORD)

**Variables de entorno**:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

**Salida de ejemplo**:
```
✓ Superusuario creado exitosamente: admin (admin@example.com)

IMPORTANTE: Cambie la contraseña del superusuario después del primer login
```

---

## Tests Implementados

### Archivo: `certificates/tests/test_management_commands.py`

**Total de tests**: 22 tests (todos pasando ✅)

#### Tests de load_default_template (7 tests)
- ✅ `test_load_default_template_creates_template`: Crea plantilla correctamente
- ✅ `test_load_default_template_does_not_overwrite_without_force`: No sobrescribe sin --force
- ✅ `test_load_default_template_overwrites_with_force`: Sobrescribe con --force
- ✅ `test_load_default_template_ensures_only_one_default`: Solo una plantilla por defecto
- ✅ `test_load_default_template_extracts_css`: Extrae CSS correctamente
- ✅ `test_load_default_template_sets_field_positions`: Configura posiciones de campos

#### Tests de generate_certificates (5 tests)
- ✅ `test_generate_certificates_success`: Genera certificados exitosamente
- ✅ `test_generate_certificates_nonexistent_event`: Falla con evento inexistente
- ✅ `test_generate_certificates_no_participants`: Maneja evento sin participantes
- ✅ `test_generate_certificates_with_force`: Regenera con --force
- ✅ `test_generate_certificates_without_force_skips_existing`: Omite existentes sin --force

#### Tests de sign_certificates (5 tests)
- ✅ `test_sign_certificates_success`: Firma certificados exitosamente
- ✅ `test_sign_certificates_nonexistent_event`: Falla con evento inexistente
- ✅ `test_sign_certificates_no_certificates`: Maneja evento sin certificados
- ✅ `test_sign_certificates_skips_already_signed`: Omite certificados ya firmados
- ✅ `test_sign_certificates_with_all_flag`: Procesa todos con --all
- ✅ `test_sign_certificates_handles_errors`: Maneja errores de firma

#### Tests de create_superuser_if_not_exists (5 tests)
- ✅ `test_create_superuser_success`: Crea superusuario exitosamente
- ✅ `test_create_superuser_skips_if_exists`: Omite si ya existe
- ✅ `test_create_superuser_requires_password`: Requiere contraseña
- ✅ `test_create_superuser_uses_defaults`: Usa valores por defecto
- ✅ `test_create_superuser_uses_environment_variables`: Usa variables de entorno

---

## Casos de Uso

### Deployment Inicial
```bash
# 1. Crear superusuario
python manage.py create_superuser_if_not_exists \
    --username admin \
    --email admin@drtcpuno.gob.pe \
    --password $ADMIN_PASSWORD

# 2. Cargar plantilla por defecto
python manage.py load_default_template

# 3. Listo para usar
```

### Workflow Completo de Certificados
```bash
# 1. Importar participantes (vía admin web)
# 2. Generar certificados
python manage.py generate_certificates --event-id 1

# 3. Firmar certificados
python manage.py sign_certificates --event-id 1

# 4. Los certificados están listos para descarga
```

### Regenerar Certificados
```bash
# Si necesita regenerar certificados (ej: cambio de plantilla)
python manage.py generate_certificates --event-id 1 --force
python manage.py sign_certificates --event-id 1
```

### CI/CD Pipeline
```bash
# En script de deployment
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
export DJANGO_SUPERUSER_PASSWORD=$SECRET_PASSWORD

python manage.py migrate
python manage.py create_superuser_if_not_exists
python manage.py load_default_template
python manage.py collectstatic --noinput
```

---

## Integración con Logging

Todos los comandos utilizan el sistema de logging implementado en Task 15:

- **generate_certificates**: Registra en logger `certificates`
- **sign_certificates**: Registra en logger `certificates.signature`
- **Logs incluyen**: Éxitos, errores, advertencias, progreso

---

## Requisitos Cumplidos

- ✅ **2.1**: Comando para generar certificados para un evento
- ✅ **5.1**: Comando para firmar certificados de un evento
- ✅ **6.1**: Comando para cargar plantilla por defecto
- ✅ **Deployment**: Comando para crear superusuario automáticamente
- ✅ **Tests**: Tests completos para todos los comandos

---

## Verificación

### Ejecutar todos los tests
```bash
python manage.py test certificates.tests.test_management_commands -v 2
```

**Resultado**: ✅ 22 tests pasados en ~6.6 segundos

### Probar comandos manualmente
```bash
# Listar comandos disponibles
python manage.py help

# Ver ayuda de un comando específico
python manage.py generate_certificates --help
python manage.py sign_certificates --help
python manage.py load_default_template --help
python manage.py create_superuser_if_not_exists --help
```

---

## Notas Adicionales

1. **Idempotencia**: Los comandos son idempotentes cuando es apropiado:
   - `load_default_template`: No sobrescribe sin --force
   - `create_superuser_if_not_exists`: No crea duplicados
   - `generate_certificates`: Requiere --force para regenerar
   - `sign_certificates`: Omite certificados ya firmados sin --all

2. **Manejo de Errores**: Todos los comandos manejan errores gracefully:
   - Validación de entrada
   - Mensajes de error claros
   - No dejan el sistema en estado inconsistente

3. **Feedback al Usuario**: Todos los comandos proporcionan:
   - Mensajes de progreso
   - Estadísticas finales
   - Advertencias cuando es necesario
   - Códigos de salida apropiados

4. **Seguridad**:
   - `create_superuser_if_not_exists` requiere contraseña obligatoriamente
   - Advertencia para cambiar contraseña después del primer login
   - No muestra contraseñas en logs o salida

---

## Estado Final

✅ **Task 16 completada exitosamente**

Todos los comandos de management están implementados, probados y documentados. El sistema está listo para operaciones administrativas automatizadas y deployment.
