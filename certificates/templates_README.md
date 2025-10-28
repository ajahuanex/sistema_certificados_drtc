# Plantilla de Certificado por Defecto

## Descripción

La plantilla por defecto (`default_certificate.html`) es un diseño profesional para certificados de capacitación de la DRTC Puno. Está optimizada para impresión en formato A4 horizontal.

## Características

### Diseño
- **Formato**: A4 horizontal (297mm x 210mm)
- **Bordes**: Doble borde decorativo (azul y gris oscuro)
- **Marca de agua**: Logo DRTC Puno en el fondo
- **Colores**: Paleta institucional (azul #2980b9, gris oscuro #2c3e50)

### Elementos Incluidos

1. **Encabezado**
   - Logo de DRTC Puno (SVG placeholder)
   - Nombre de la institución
   - Subtítulo con ubicación

2. **Cuerpo del Certificado**
   - Título "CERTIFICADO" destacado
   - Nombre completo del participante (en mayúsculas)
   - DNI del participante
   - Tipo de asistente (badge con color)
   - Nombre del evento

3. **Pie de Página**
   - Código QR para verificación
   - Línea de firma del Director Regional
   - Fecha de emisión del certificado

### Variables de Plantilla

La plantilla utiliza las siguientes variables de Django:

- `{{ participant.full_name }}` - Nombre completo del participante
- `{{ participant.dni }}` - DNI del participante
- `{{ participant.get_attendee_type_display }}` - Tipo de asistente (ASISTENTE, PONENTE, ORGANIZADOR)
- `{{ event.name }}` - Nombre del evento
- `{{ event.event_date|date:"d/m/Y" }}` - Fecha del evento
- `{{ qr_code }}` - Ruta de la imagen del código QR

### Posiciones de Campos

Las posiciones de los campos están definidas en el modelo `CertificateTemplate`:

```python
field_positions = {
    'participant_name': {'x': 'center', 'y': '80mm'},
    'participant_dni': {'x': 'center', 'y': '95mm'},
    'event_name': {'x': 'center', 'y': '125mm'},
    'event_date': {'x': '240mm', 'y': '180mm'},
    'attendee_type': {'x': 'center', 'y': '110mm'},
    'qr_code': {'x': '30mm', 'y': '165mm'},
    'signature': {'x': 'center', 'y': '175mm'}
}
```

## Cargar la Plantilla en la Base de Datos

Para cargar la plantilla por defecto en la base de datos, ejecute:

```bash
python manage.py load_default_template
```

### Opciones del Comando

- `--force`: Actualiza la plantilla por defecto si ya existe

```bash
python manage.py load_default_template --force
```

## Personalización

### Cambiar el Logo

Reemplace el SVG placeholder en la sección `.logo` con su logo real:

```html
<div class="logo">
    <img src="path/to/logo.png" alt="Logo DRTC Puno">
</div>
```

### Modificar Colores

Los colores principales están definidos en el CSS:

- Color primario: `#2980b9` (azul)
- Color secundario: `#2c3e50` (gris oscuro)
- Color de acento: `#3498db` (azul claro)

### Ajustar Tamaños de Fuente

Los tamaños de fuente están definidos en puntos (pt):

- Título: `32pt`
- Nombre del participante: `24pt`
- Nombre del evento: `16pt`
- Texto general: `14pt`

## Generación de PDF

La plantilla está optimizada para conversión a PDF usando WeasyPrint. Los estilos de impresión están configurados con:

```css
@page {
    size: A4 landscape;
    margin: 0;
}

@media print {
    body {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}
```

## Verificación

El código QR en el certificado permite verificar su autenticidad escaneándolo con cualquier lector de códigos QR. El código redirige a una URL de verificación única del certificado.

## Requisitos

- Django 4.2+
- WeasyPrint (para generación de PDF)
- qrcode (para generación de códigos QR)
- Pillow (para procesamiento de imágenes)
