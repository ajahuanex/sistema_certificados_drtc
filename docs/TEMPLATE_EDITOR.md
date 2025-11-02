# Editor de Plantillas Avanzado

## Introducción

El Editor de Plantillas Avanzado es una herramienta visual que permite crear y editar plantillas de certificados de manera intuitiva, sin necesidad de conocimientos técnicos de HTML o CSS.

## Características Principales

### 🎨 Editor Visual WYSIWYG
- Canvas interactivo con drag-and-drop
- Posicionamiento preciso de elementos
- Vista previa en tiempo real
- Sistema de grillas y guías de alineación

### 📝 Elementos Soportados
- **Texto**: Texto libre con formato personalizable
- **Variables**: Campos dinámicos que se reemplazan automáticamente
- **Imágenes**: Logos, firmas, sellos desde la biblioteca
- **Códigos QR**: Para verificación de certificados
- **Fórmulas LaTeX**: Notación matemática y científica

### 🎯 Variables Disponibles
- `{{participant_name}}` - Nombre del participante
- `{{participant_dni}}` - DNI del participante
- `{{event_name}}` - Nombre del evento
- `{{event_date}}` - Fecha del evento
- `{{certificate_uuid}}` - UUID único del certificado
- `{{attendee_type}}` - Tipo de asistente

### 📚 Biblioteca de Assets
- Gestión centralizada de recursos
- Categorización automática (Logos, Firmas, Sellos, Fondos)
- Reutilización entre plantillas
- Formatos soportados: PNG, JPG, JPEG, SVG

## Guía de Uso

### Acceso al Editor

1. Navegar al panel de administración
2. Ir a "Plantillas de Certificados"
3. Hacer clic en "Agregar plantilla" o editar una existente
4. Seleccionar "Editor Visual"

### Creación de una Plantilla

#### 1. Configuración Inicial
```
- Nombre: Asignar un nombre descriptivo
- Dimensiones: Configurar ancho y alto del canvas (por defecto A4 landscape: 842×595px)
- Fondo: Seleccionar imagen de fondo opcional
```

#### 2. Agregar Elementos

**Elemento de Texto:**
1. Hacer clic en el botón "Texto" en la barra de herramientas
2. Posicionar el elemento en el canvas
3. Editar el contenido en el panel de propiedades
4. Configurar fuente, tamaño, color y alineación

**Variables Dinámicas:**
1. Hacer clic en "Variable" o seleccionar de la lista
2. Elegir la variable deseada (ej: `{{participant_name}}`)
3. El texto se reemplazará automáticamente al generar certificados

**Imágenes:**
1. Subir imagen a la biblioteca o seleccionar existente
2. Arrastrar desde la biblioteca al canvas
3. Redimensionar y posicionar según necesidad

**Fórmulas LaTeX:**
1. Hacer clic en "LaTeX" (símbolo ∑)
2. Escribir la fórmula en sintaxis LaTeX
3. Vista previa automática
4. Ejemplos:
   - Inline: `$E = mc^2$`
   - Display: `$$\int_0^1 x^2 dx = \frac{1}{3}$$`

#### 3. Gestión de Capas
- Usar el panel de capas para organizar elementos
- Controlar qué elementos aparecen encima de otros
- Bloquear elementos para evitar modificaciones accidentales

#### 4. Vista Previa
- Hacer clic en "Vista Previa" para ver el resultado final
- Probar con diferentes datos de ejemplo
- Generar PDF de prueba

### Funciones Avanzadas

#### Exportar/Importar Plantillas
```
Exportar:
1. Abrir plantilla en el editor
2. Hacer clic en "Exportar"
3. Se descarga un archivo ZIP con todos los recursos

Importar:
1. Hacer clic en "Importar Plantilla"
2. Seleccionar archivo ZIP exportado
3. Confirmar importación
```

#### Auto-guardado
- Las plantillas se guardan automáticamente cada 30 segundos
- Indicador visual del estado de guardado
- Backup local en caso de pérdida de conexión

#### Historial (Undo/Redo)
- `Ctrl+Z`: Deshacer última acción
- `Ctrl+Y` o `Ctrl+Shift+Z`: Rehacer
- Historial de hasta 50 acciones

## Sintaxis LaTeX Soportada

### Operadores Básicos
```latex
$\frac{a}{b}$          # Fracción
$\sqrt{x}$              # Raíz cuadrada
$\sqrt[n]{x}$           # Raíz n-ésima
$x^2$                   # Exponente
$x_i$                   # Subíndice
```

### Símbolos Matemáticos
```latex
$\alpha, \beta, \gamma$ # Letras griegas
$\infty$                # Infinito
$\pm, \mp$              # Más/menos
$\leq, \geq, \neq$      # Comparadores
$\sum, \int, \prod$     # Operadores
```

### Funciones
```latex
$\sin(x), \cos(x), \tan(x)$  # Trigonométricas
$\log(x), \ln(x), \exp(x)$   # Logarítmicas
$\lim_{x \to 0} f(x)$         # Límites
```

### Matrices
```latex
$$\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}$$
```

### Fórmulas Complejas
```latex
$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$

$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
```

## Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+S` | Guardar plantilla |
| `Ctrl+Z` | Deshacer |
| `Ctrl+Y` | Rehacer |
| `Ctrl+C` | Copiar elemento |
| `Ctrl+V` | Pegar elemento |
| `Delete` | Eliminar elemento seleccionado |
| `Ctrl+]` | Traer al frente |
| `Ctrl+[` | Enviar atrás |

## Mejores Prácticas

### Diseño
1. **Usar grillas**: Activar la grilla para alineación precisa
2. **Jerarquía visual**: Usar diferentes tamaños de fuente para crear jerarquía
3. **Espaciado consistente**: Mantener espacios uniformes entre elementos
4. **Contraste**: Asegurar buen contraste entre texto y fondo

### Organización
1. **Nombres descriptivos**: Asignar nombres claros a elementos y plantillas
2. **Capas ordenadas**: Organizar elementos en capas lógicas
3. **Biblioteca limpia**: Mantener assets organizados por categorías
4. **Backup regular**: Exportar plantillas importantes regularmente

### Performance
1. **Optimizar imágenes**: Usar imágenes del tamaño apropiado
2. **Limitar elementos**: No sobrecargar con demasiados elementos
3. **Formatos eficientes**: Preferir PNG para logos, JPG para fotos

## Resolución de Problemas

### Problemas Comunes

**El texto no se ve correctamente:**
- Verificar que la fuente esté disponible
- Comprobar el color del texto vs fondo
- Ajustar el tamaño del elemento contenedor

**LaTeX no se renderiza:**
- Verificar sintaxis con el validador
- Usar delimitadores correctos ($...$ o $$...$$)
- Evitar comandos no soportados

**Imagen no aparece:**
- Verificar que el asset esté subido correctamente
- Comprobar formato de archivo (PNG, JPG, SVG)
- Verificar permisos del archivo

**Vista previa no coincide con PDF:**
- Regenerar vista previa
- Verificar configuración de renderizado
- Comprobar que todos los assets estén disponibles

### Limitaciones Conocidas

1. **LaTeX**: Solo se soporta un subconjunto de comandos matemáticos
2. **Fuentes**: Limitado a fuentes del sistema
3. **Animaciones**: No se soportan elementos animados
4. **Tamaño de archivo**: Límite de 10MB para assets individuales

## API del Editor

### Endpoints Principales

```http
GET    /api/templates/                    # Listar plantillas
POST   /api/templates/                    # Crear plantilla
GET    /api/templates/{id}/               # Obtener plantilla
PUT    /api/templates/{id}/               # Actualizar plantilla
DELETE /api/templates/{id}/               # Eliminar plantilla

GET    /api/templates/{id}/preview/       # Vista previa
POST   /api/templates/{id}/export/        # Exportar plantilla
POST   /api/templates/import/             # Importar plantilla

GET    /api/elements/                     # Listar elementos
POST   /api/elements/                     # Crear elemento
PUT    /api/elements/{id}/                # Actualizar elemento

GET    /api/assets/                       # Listar assets
POST   /api/assets/                       # Subir asset

POST   /api/latex/validate/               # Validar LaTeX
POST   /api/latex/render/                 # Renderizar LaTeX
```

### Ejemplo de Uso de API

```javascript
// Crear nueva plantilla
const template = await fetch('/api/templates/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        name: 'Mi Plantilla',
        canvas_width: 842,
        canvas_height: 595
    })
});

// Agregar elemento de texto
const element = await fetch('/api/elements/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        template: templateId,
        element_type: 'TEXT',
        name: 'Título',
        position_x: 100,
        position_y: 100,
        width: 400,
        height: 50,
        content: 'CERTIFICADO DE PARTICIPACIÓN'
    })
});

// Generar vista previa
const preview = await fetch(`/api/templates/${templateId}/preview/?format=pdf`);
const pdfBlob = await preview.blob();
```

## Integración con el Sistema

### Uso en Generación de Certificados

El editor se integra automáticamente con el sistema de generación de certificados:

1. **Selección de Plantilla**: Al crear un evento, seleccionar plantilla del editor
2. **Generación Automática**: Los certificados usan la plantilla visual
3. **Variables Dinámicas**: Se reemplazan automáticamente con datos reales
4. **PDF Final**: Se genera usando el motor de renderizado

### Migración de Plantillas Antiguas

Las plantillas HTML existentes siguen funcionando:
- Se mantiene compatibilidad con plantillas HTML
- Se puede migrar gradualmente al editor visual
- Ambos sistemas coexisten sin problemas

## Soporte y Ayuda

### Documentación Adicional
- [Guía de LaTeX](LATEX_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

### Contacto
Para soporte técnico o reportar problemas, contactar al administrador del sistema.

---

*Última actualización: Noviembre 2024*
*Versión del Editor: 1.0*
##
 Integración con el Sistema Existente

### Compatibilidad Total

El editor visual está completamente integrado con el sistema existente de certificados:

- **Detección automática**: El sistema detecta si una plantilla es visual o HTML tradicional
- **Generación unificada**: Mismo proceso para generar certificados independientemente del tipo de plantilla
- **Variables compatibles**: Las mismas variables funcionan en ambos sistemas
- **Administración centralizada**: Gestión desde el mismo panel de admin

### Tipos de Plantillas

El sistema ahora soporta dos tipos de plantillas:

1. **🎨 Plantillas Visuales**: Creadas con el editor visual
   - Renderizado con WeasyPrint
   - Elementos posicionados absolutamente
   - Soporte completo para LaTeX y assets

2. **📝 Plantillas HTML**: Plantillas tradicionales
   - Renderizado con ReportLab (método original)
   - Compatibilidad total mantenida
   - Migración automática disponible

### Migración de Plantillas HTML

#### Migración Individual

Para migrar una plantilla HTML existente:

1. Ir a **Admin → Plantillas de Certificados**
2. Localizar la plantilla HTML (marcada con 📝)
3. Hacer clic en **"🔄 Migrar"**
4. Revisar el preview de elementos que se crearán
5. Confirmar la migración

El proceso:
- ✅ Preserva el HTML original como comentario
- ✅ Crea elementos visuales equivalentes
- ✅ Mapea variables automáticamente
- ✅ Configura dimensiones del canvas

#### Migración Masiva

Para migrar todas las plantillas HTML:

1. En la lista de plantillas, hacer clic en **"🔄 Migrar X plantillas al editor visual"**
2. Revisar el resumen de plantillas a migrar
3. Confirmar la migración masiva

**Desde línea de comandos:**
```bash
# Migrar todas las plantillas sin elementos visuales
python manage.py migrate_templates --all

# Solo preview sin hacer cambios
python manage.py migrate_templates --all --preview

# Migrar plantilla específica
python manage.py migrate_templates --template-id 1

# Forzar migración incluso si ya tiene elementos
python manage.py migrate_templates --all --force
```

### Mapeo de Variables

El sistema mapea automáticamente las variables entre formatos:

| Variable HTML Original | Variable Visual | Descripción |
|----------------------|-----------------|-------------|
| `{{ full_name }}` | `{{participant_name}}` | Nombre del participante |
| `{{ dni }}` | `{{participant_dni}}` | DNI del participante |
| `{{ event_name }}` | `{{event_name}}` | Nombre del evento |
| `{{ event_date }}` | `{{event_date}}` | Fecha del evento |
| `{{ attendee_type }}` | `{{attendee_type}}` | Tipo de asistente |

### Generación de Certificados

El proceso de generación es transparente:

```python
# El mismo código funciona para ambos tipos de plantilla
service = CertificateGeneratorService()
certificate = service.generate_certificate(participant, user=request.user)
```

**Flujo interno:**
1. El sistema verifica si la plantilla tiene elementos visuales
2. **Si es visual**: Usa `TemplateRenderingService` con WeasyPrint
3. **Si es HTML**: Usa el método original con ReportLab
4. **Fallback**: Si falla el visual, intenta el método simple

### Administración de Eventos

Los eventos pueden usar cualquier tipo de plantilla:

- **Campo unificado**: Mismo selector `template` en el modelo Event
- **Indicador visual**: Las plantillas se marcan como 🎨 Visual o 📝 HTML
- **Compatibilidad**: Eventos existentes siguen funcionando sin cambios

### APIs REST Integradas

Las APIs están completamente integradas:

```bash
# Listar todas las plantillas (visuales y HTML)
GET /api/templates/

# Obtener plantilla específica con elementos si es visual
GET /api/templates/{id}/

# Vista previa funciona para ambos tipos
GET /api/templates/{id}/preview/?format=pdf
```

## Comandos de Gestión

### Migración de Plantillas

```bash
# Ver ayuda completa
python manage.py migrate_templates --help

# Migrar todas las plantillas HTML
python manage.py migrate_templates --all

# Preview de migración sin cambios
python manage.py migrate_templates --all --preview

# Migrar plantilla específica
python manage.py migrate_templates --template-id 1

# Forzar migración incluso si ya tiene elementos
python manage.py migrate_templates --template-id 1 --force

# No preservar HTML original
python manage.py migrate_templates --all --no-preserve
```

### Verificación del Sistema

```bash
# Verificar integridad de plantillas
python manage.py check_template_integrity

# Limpiar assets no utilizados
python manage.py cleanup_unused_assets

# Generar certificados de prueba
python manage.py test_certificate_generation
```

## Solución de Problemas de Integración

### Plantillas No Migran Correctamente

**Problema**: La migración no crea elementos esperados

**Soluciones**:
1. Verificar que el HTML sea válido
2. Usar variables Django estándar (`{{ variable }}`)
3. Revisar elementos creados manualmente después de migración
4. Usar `--preview` para ver qué se creará antes de migrar

### Certificados No Se Generan

**Problema**: Error al generar certificados con plantillas visuales

**Soluciones**:
1. Verificar que WeasyPrint esté instalado correctamente
2. Comprobar que todos los assets existen
3. Revisar logs de Django para errores específicos
4. Probar con plantilla HTML como fallback

### Variables No Se Reemplazan

**Problema**: Las variables aparecen literalmente en el PDF

**Soluciones**:
1. Usar sintaxis correcta: `{{variable_name}}`
2. Verificar que la variable esté en la lista de variables disponibles
3. Comprobar mapeo de variables en el servicio de renderizado
4. Revisar datos del participante

### Assets No Se Muestran

**Problema**: Imágenes no aparecen en el PDF generado

**Soluciones**:
1. Verificar que el archivo del asset existe
2. Comprobar permisos de lectura del archivo
3. Usar formatos compatibles (PNG, JPG, SVG)
4. Verificar tamaño del archivo (máximo 10MB)

## Mejores Prácticas de Integración

### Migración Gradual

1. **Fase 1**: Migrar plantillas de prueba
2. **Fase 2**: Migrar plantillas menos críticas
3. **Fase 3**: Migrar plantillas principales
4. **Fase 4**: Mantener algunas HTML como respaldo

### Gestión de Assets

1. **Organización**: Crear categorías claras antes de migrar
2. **Nomenclatura**: Usar nombres descriptivos para assets
3. **Respaldo**: Exportar plantillas importantes regularmente
4. **Limpieza**: Eliminar assets no utilizados periódicamente

### Monitoreo

1. **Logs**: Revisar logs de generación de certificados
2. **Performance**: Monitorear tiempos de renderizado
3. **Errores**: Configurar alertas para fallos de generación
4. **Uso**: Trackear qué plantillas se usan más

### Capacitación

1. **Usuarios**: Entrenar a administradores en el nuevo editor
2. **Documentación**: Mantener guías actualizadas
3. **Soporte**: Establecer proceso para resolver dudas
4. **Feedback**: Recopilar comentarios para mejoras

## Roadmap de Integración

### Completado ✅

- [x] Integración con CertificateGeneratorService
- [x] Detección automática de tipo de plantilla
- [x] Migración de plantillas HTML existentes
- [x] Compatibilidad con variables del sistema
- [x] Administración unificada en Django Admin
- [x] APIs REST integradas
- [x] Comandos de gestión
- [x] Tests de integración
- [x] Documentación completa

### Próximas Mejoras 🚀

- [ ] Migración automática en background
- [ ] Cache de renderizado para mejor performance
- [ ] Plantillas predefinidas por industria
- [ ] Editor colaborativo en tiempo real
- [ ] Versionado de plantillas
- [ ] Análisis de uso de plantillas
- [ ] Integración con sistemas externos
- [ ] Plantillas responsive para diferentes tamaños

## Soporte y Mantenimiento

### Logs Importantes

```bash
# Logs de generación de certificados
tail -f logs/certificates.log

# Logs de migración de plantillas
tail -f logs/django.log | grep "migrate_templates"

# Logs de renderizado visual
tail -f logs/django.log | grep "TemplateRenderingService"
```

### Métricas de Monitoreo

- Tiempo promedio de generación de certificados
- Tasa de éxito de renderizado visual vs HTML
- Uso de plantillas por tipo
- Errores de migración
- Performance de APIs REST

### Contacto y Soporte

Para problemas específicos de integración:

1. **Revisar logs** de Django y certificados
2. **Consultar documentación** técnica
3. **Ejecutar comandos de diagnóstico**
4. **Reportar issues** con información detallada

La integración está diseñada para ser transparente y mantener compatibilidad total con el sistema existente, permitiendo una transición gradual al nuevo editor visual.
## 📐 Tam
años de Canvas y Orientaciones

### Tamaños Estándar Soportados

#### A4 (210 × 297 mm) - Recomendado
- **A4 Horizontal**: 842×595 px - **Ideal para certificados** 📜
  - Orientación: Apaisada (Landscape)
  - Uso: Certificados de capacitación, reconocimientos
  - Proporción: 1.42:1

- **A4 Vertical**: 595×842 px - Para documentos largos 📋
  - Orientación: Vertical (Portrait)
  - Uso: Diplomas, constancias, cartas oficiales
  - Proporción: 1:1.42

#### Carta US (216 × 279 mm)
- **Carta Horizontal**: 792×612 px
  - Orientación: Apaisada
  - Uso: Certificados estándar US

- **Carta Vertical**: 612×792 px
  - Orientación: Vertical
  - Uso: Documentos oficiales US

#### Formatos Especiales
- **Cuadrado Grande**: 800×800 px
  - Uso: Badges digitales, sellos, logos
  - Proporción: 1:1

- **Panorámico**: 1200×600 px
  - Uso: Banners, headers, certificados especiales
  - Proporción: 2:1

### Configuración de Resolución

#### Para Pantalla (72 DPI)
- Tamaños base mostrados arriba
- Optimizado para visualización web
- Archivos más ligeros

#### Para Impresión (300 DPI)
- A4 Horizontal: 3508×2480 px
- A4 Vertical: 2480×3508 px
- Conversión automática en el renderizado
- Calidad profesional para impresión

### Recomendaciones por Tipo de Documento

| Tipo de Documento | Tamaño Recomendado | Orientación | Razón |
|-------------------|-------------------|-------------|--------|
| Certificados de Capacitación | A4 Horizontal | Landscape | Más espacio para logos y firmas |
| Diplomas Académicos | A4 Vertical | Portrait | Formato tradicional académico |
| Reconocimientos | A4 Horizontal | Landscape | Presentación más impactante |
| Constancias | A4 Vertical | Portrait | Formato oficial estándar |
| Badges Digitales | Cuadrado | Square | Compatibilidad con redes sociales |
| Certificados Corporativos | A4 Horizontal | Landscape | Espacio para branding corporativo |

### Configuración en el Editor

#### Crear Nueva Plantilla
1. Seleccionar tamaño predefinido del dropdown
2. O ingresar dimensiones personalizadas
3. El sistema detecta automáticamente la orientación
4. Vista previa se ajusta al tamaño seleccionado

#### Cambiar Tamaño de Plantilla Existente
1. Ir a configuración de plantilla
2. Modificar `canvas_width` y `canvas_height`
3. Los elementos se mantienen en posiciones relativas
4. Revisar posicionamiento después del cambio

### Mejores Prácticas

#### Diseño Responsivo
- Usar posiciones relativas cuando sea posible
- Considerar márgenes de seguridad (50px desde bordes)
- Probar en ambas orientaciones si es necesario

#### Elementos de Texto
- **A4 Horizontal**: Títulos hasta 48px, texto hasta 16px
- **A4 Vertical**: Títulos hasta 36px, texto hasta 14px
- Mantener legibilidad en impresión

#### Imágenes y Logos
- Usar imágenes vectoriales (SVG) cuando sea posible
- Resolución mínima: 150 DPI para el tamaño final
- Considerar espacio para firmas y sellos

#### Códigos QR
- Tamaño mínimo: 80×80 px
- Posición recomendada: Esquina inferior derecha
- Dejar espacio blanco alrededor (10px mínimo)

### Conversión Automática

El sistema maneja automáticamente:
- **Escalado para impresión**: 72 DPI → 300 DPI
- **Optimización de fuentes**: Selección automática según disponibilidad
- **Ajuste de elementos**: Posicionamiento preciso en diferentes tamaños
- **Calidad de imágenes**: Interpolación inteligente para alta resolución

### Solución de Problemas de Tamaños

#### Elementos Fuera del Canvas
- Verificar que `position_x + width ≤ canvas_width`
- Verificar que `position_y + height ≤ canvas_height`
- Usar herramientas de alineación del editor

#### Texto Cortado
- Aumentar altura del elemento de texto
- Reducir tamaño de fuente
- Usar salto de línea automático

#### Imágenes Distorsionadas
- Mantener proporción original
- Usar `object-fit: contain` en CSS
- Verificar resolución de imagen fuente

#### PDF No Imprime Correctamente
- Verificar configuración de página en CSS
- Comprobar márgenes de impresora
- Usar modo de impresión sin márgenes si es necesario