# Task 15: Sistema de Logging - Resumen de Implementación

## Objetivo
Implementar un sistema completo de logging para la aplicación de certificados, con configuración de RotatingFileHandler y loggers específicos para diferentes componentes.

## Cambios Realizados

### 1. Configuración de Logging en Settings

#### `config/settings/base.py`
- Agregada configuración completa de LOGGING con:
  - **Formatters**: `verbose` y `simple` para diferentes niveles de detalle
  - **Handlers**:
    - `console`: Para salida en consola
    - `file`: RotatingFileHandler para logs generales (10MB, 5 backups)
    - `signature_file`: RotatingFileHandler para logs de firma digital (10MB, 5 backups)
  - **Loggers**:
    - `certificates`: Nivel INFO, escribe en console y file
    - `certificates.signature`: Nivel DEBUG, escribe en console y signature_file

#### `config/settings/development.py`
- Actualizada configuración de logging para desarrollo
- Mantiene la misma estructura que base.py
- Incluye handlers de archivo para desarrollo
- Logger `certificates` en nivel INFO
- Logger `certificates.signature` en nivel DEBUG

### 2. Logging en Servicios

Los servicios ya tenían logging implementado correctamente:

#### `certificates/services/excel_processor.py`
- Logger: `certificates`
- **INFO**: Eventos creados, participantes creados/actualizados, importación completada
- **WARNING**: Filas inválidas durante importación
- **ERROR**: Archivo inválido, errores al procesar filas

#### `certificates/services/certificate_generator.py`
- Logger: `certificates`
- **DEBUG**: Plantilla renderizada
- **INFO**: PDF generado (con tamaño), certificado generado, generación masiva completada
- **WARNING**: Certificado ya existe para participante
- **ERROR**: Errores al generar certificados en bulk

#### `certificates/services/digital_signature.py`
- Logger: `certificates.signature`
- **DEBUG**: Enviando PDF al servicio de firma, esperando antes de reintentar
- **INFO**: Intento de firma, PDF firmado recibido, certificado firmado exitosamente, estado actualizado, firma masiva iniciada/completada
- **WARNING**: Certificado ya firmado, intento de firma falló
- **ERROR**: Falló la firma después de todos los reintentos

### 3. Tests de Logging

#### `certificates/tests/test_logging.py`
Creado archivo completo de tests con 13 casos de prueba:

**Tests de ExcelProcessorService:**
- `test_excel_processor_logs_info`: Verifica logs INFO en importación exitosa
- `test_excel_processor_logs_errors`: Verifica logs ERROR con archivo inválido
- `test_excel_processor_logs_warnings`: Verifica logs WARNING con filas inválidas

**Tests de CertificateGeneratorService:**
- `test_certificate_generator_logs_info`: Verifica logs INFO en generación exitosa
- `test_certificate_generator_logs_errors`: Verifica logs ERROR cuando hay errores
- `test_certificate_generator_bulk_logs`: Verifica logs en generación masiva

**Tests de DigitalSignatureService:**
- `test_digital_signature_logs_info`: Verifica logs INFO en firma exitosa
- `test_digital_signature_logs_debug`: Verifica logs DEBUG durante firma
- `test_digital_signature_logs_errors`: Verifica logs ERROR cuando falla la firma
- `test_digital_signature_logs_warnings`: Verifica logs WARNING en reintentos
- `test_digital_signature_bulk_logs`: Verifica logs en firma masiva

**Tests de Configuración:**
- `test_logging_configuration_exists`: Verifica que existe configuración de logging
- `test_logging_handlers_configured`: Verifica que los handlers están configurados correctamente

## Estructura de Archivos de Log

```
logs/
├── certificates.log      # Logs generales de la aplicación
├── signature.log         # Logs específicos de firma digital
└── django.log           # Logs de Django (si existe)
```

## Características del Sistema de Logging

### RotatingFileHandler
- **Tamaño máximo por archivo**: 10MB
- **Número de backups**: 5
- **Total de espacio**: ~60MB por logger (archivo actual + 5 backups)
- **Rotación automática**: Cuando el archivo alcanza 10MB

### Niveles de Log por Componente

| Componente | Logger | Nivel | Archivo |
|------------|--------|-------|---------|
| Excel Processor | certificates | INFO | certificates.log |
| Certificate Generator | certificates | INFO | certificates.log |
| Digital Signature | certificates.signature | DEBUG | signature.log |

### Formato de Logs

**Verbose (archivos):**
```
{levelname} {asctime} {module} {process:d} {thread:d} {message}
```

**Simple (consola):**
```
{levelname} {asctime} {message}
```

## Ejemplos de Logs Generados

### Importación de Excel
```
INFO 2025-10-28 05:17:01,735 excel_processor 17604 22464 Evento creado: Evento Test - 2024-01-15
INFO 2025-10-28 05:17:01,756 excel_processor 17604 22464 Participante creado: Juan Pérez (12345678)
INFO 2025-10-28 05:17:01,775 excel_processor 17604 22464 Importación completada: 10 éxitos, 0 errores
```

### Generación de Certificados
```
INFO 2025-10-28 05:17:04,280 certificate_generator 17604 22464 PDF generado: 8421 bytes
INFO 2025-10-28 05:17:04,283 certificate_generator 17604 22464 Certificado generado: ecc24433-5d77-4f83-9243-0b5cee56011f para Juan Pérez
```

### Firma Digital
```
DEBUG 2025-10-28 05:17:05,168 digital_signature 17604 22464 Enviando PDF al servicio de firma: http://localhost:8080/api/sign
INFO 2025-10-28 05:17:05,174 digital_signature 17604 22464 PDF firmado recibido: 8457 bytes
INFO 2025-10-28 05:17:05,177 digital_signature 17604 22464 Certificado a49882eb-8319-4254-a682-868bb2b6b6d6 firmado exitosamente
```

## Verificación

### Tests
```bash
python manage.py test certificates.tests.test_logging -v 2
```

**Resultado**: ✅ 13 tests pasados

### Archivos de Log
- ✅ `logs/certificates.log` creado y funcionando
- ✅ `logs/signature.log` creado y funcionando
- ✅ Rotación automática configurada
- ✅ Formato verbose en archivos
- ✅ Formato simple en consola

## Requisitos Cumplidos

- ✅ **8.1**: Configurar LOGGING en settings con RotatingFileHandler
- ✅ **8.2**: Crear logger 'certificates' para eventos generales
- ✅ **8.3**: Crear logger 'certificates.signature' para firma digital
- ✅ **8.4**: Agregar logging en ExcelProcessorService (info y errores)
- ✅ **8.5**: Agregar logging en CertificateGeneratorService (info y errores)
- ✅ **8.6**: Agregar logging en DigitalSignatureService (debug, info y errores)
- ✅ **8.7**: Escribir tests que verifican que se generan logs

## Notas Adicionales

1. **Logging en Producción**: La configuración en `production.py` puede ajustarse para:
   - Cambiar niveles de log (ej: WARNING en lugar de INFO)
   - Agregar handlers adicionales (ej: syslog, email para errores críticos)
   - Configurar rutas absolutas para archivos de log

2. **Monitoreo**: Los archivos de log pueden ser monitoreados con herramientas como:
   - `tail -f logs/certificates.log` (Linux/Mac)
   - `Get-Content logs\certificates.log -Wait` (Windows PowerShell)
   - Herramientas de monitoreo como Logstash, Splunk, etc.

3. **Auditoría**: Además del logging, el sistema usa el modelo `AuditLog` para registrar acciones importantes en la base de datos, proporcionando una capa adicional de auditoría.

## Estado Final

✅ **Task 15 completada exitosamente**

Todos los componentes del sistema de logging están implementados, configurados y probados. El sistema está listo para registrar eventos en desarrollo y producción.
