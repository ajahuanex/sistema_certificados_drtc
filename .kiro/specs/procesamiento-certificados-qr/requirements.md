# Requirements Document

## Introduction

Este documento define los requisitos para implementar un sistema de procesamiento de certificados PDF que permite importar certificados existentes, agregarles códigos QR con URLs de preview, exportarlos para firma digital externa, e importar los certificados finales firmados.

## Requirements

### Requirement 1: Importación de Certificados PDF Base

**User Story:** Como administrador, quiero importar certificados PDF existentes (sin QR) para procesarlos en el sistema, para poder agregarles códigos QR y gestionar el flujo de firma digital.

#### Acceptance Criteria

1. WHEN el administrador accede a la función de importación THEN el sistema SHALL mostrar una interfaz para subir múltiples archivos PDF
2. WHEN se suben archivos PDF THEN el sistema SHALL extraer automáticamente el nombre del participante del nombre del archivo o contenido del PDF
3. WHEN se procesa cada PDF THEN el sistema SHALL crear un registro de certificado con estado "PENDIENTE_QR"
4. IF el nombre no se puede extraer automáticamente THEN el sistema SHALL permitir mapeo manual de archivos a participantes
5. WHEN la importación es exitosa THEN el sistema SHALL mostrar un resumen de certificados importados

### Requirement 2: Generación de Códigos QR con URL de Preview

**User Story:** Como administrador, quiero que el sistema genere automáticamente códigos QR para cada certificado importado, para que los usuarios puedan acceder al preview del certificado.

#### Acceptance Criteria

1. WHEN se procesa un certificado THEN el sistema SHALL generar un código QR único que contenga la URL de preview
2. WHEN se genera el QR THEN la URL SHALL seguir el formato: `{domain}/certificado/{uuid}/preview`
3. WHEN se crea el QR THEN el sistema SHALL usar el servicio QR existente con configuración optimizada para PDFs
4. WHEN se genera el QR THEN el sistema SHALL almacenar la imagen QR en el sistema de archivos
5. IF la generación del QR falla THEN el sistema SHALL registrar el error y permitir reintento

### Requirement 3: Inserción de QR en Certificados PDF

**User Story:** Como administrador, quiero que el sistema inserte automáticamente los códigos QR generados en los certificados PDF, para crear las versiones con QR listas para firma.

#### Acceptance Criteria

1. WHEN se tiene un certificado y su QR THEN el sistema SHALL insertar el QR en una posición configurable del PDF
2. WHEN se inserta el QR THEN el sistema SHALL mantener la calidad y formato original del PDF
3. WHEN se procesa el PDF THEN el sistema SHALL crear una nueva versión con sufijo "_con_qr.pdf"
4. WHEN la inserción es exitosa THEN el sistema SHALL actualizar el estado del certificado a "CON_QR"
5. IF la inserción falla THEN el sistema SHALL mantener el archivo original y registrar el error
