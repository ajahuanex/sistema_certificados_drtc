# Design Document

## Overview

El Editor Avanzado de Plantillas es un sistema visual e interactivo que permite a los administradores diseñar certificados PDF personalizados sin necesidad de escribir código. El sistema se compone de tres partes principales:

1. **Frontend Editor**: Interfaz visual drag-and-drop construida con JavaScript vanilla y Canvas API
2. **Backend API**: Endpoints Django REST para gestionar plantillas, elementos y renderizado
3. **Rendering Engine**: Motor de renderizado que convierte el diseño visual a PDF usando WeasyPrint y MathJax para LaTeX

El sistema extiende el modelo `CertificateTemplate` existente agregando capacidades de edición visual, gestión de elementos gráficos, y renderizado de contenido matemático.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Interface                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Template   │  │   Element    │  │   Preview    │     │
│  │    Editor    │  │   Library    │  │    Panel     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Template   │  │   Element    │  │   Rendering  │     │
│  │     API      │  │     API      │  │    Service   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Certificate  │  │   Template   │  │   Template   │     │
│  │   Template   │  │   Element    │  │    Asset     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- JavaScript ES6+ (vanilla, no frameworks)
- Fabric.js para canvas interactivo
- MathJax 3.x para renderizado LaTeX
- CSS Grid/Flexbox para layout

**Backend:**
- Django 4.x
- Django REST Framework para APIs
- WeasyPrint para generación PDF
- Pillow para procesamiento de imágenes
- PyMuPDF (fitz) para manipulación PDF

**Storage:**
- PostgreSQL para datos estructurados
- Sistema de archivos para imágenes y PDFs
- JSONField para configuración de elementos



## Components and Interfaces

### 1. Data Models

#### TemplateElement Model
```python
class TemplateElement(models.Model):
    """Elemento individual en una plantilla (texto, imagen, QR, etc.)"""
    ELEMENT_TYPES = [
        ('TEXT', 'Texto'),
        ('IMAGE', 'Imagen'),
        ('QR', 'Código QR'),
        ('LATEX', 'Fórmula LaTeX'),
        ('VARIABLE', 'Variable Dinámica'),
    ]
    
    template = ForeignKey(CertificateTemplate)
    element_type = CharField(choices=ELEMENT_TYPES)
    name = CharField(max_length=200)
    
    # Posicionamiento
    position_x = IntegerField()  # píxeles desde izquierda
    position_y = IntegerField()  # píxeles desde arriba
    width = IntegerField()
    height = IntegerField()
    rotation = FloatField(default=0)  # grados
    z_index = IntegerField(default=0)  # orden de capas
    
    # Contenido
    content = TextField()  # texto, LaTeX, o referencia a asset
    variables = JSONField(default=dict)  # variables dinámicas
    
    # Estilo
    style_config = JSONField(default=dict)  # fuente, color, etc.
    
    # Metadatos
    is_locked = BooleanField(default=False)
    is_visible = BooleanField(default=True)
```

#### TemplateAsset Model
```python
class TemplateAsset(models.Model):
    """Recursos reutilizables (imágenes, logos, firmas)"""
    ASSET_TYPES = [
        ('BACKGROUND', 'Fondo'),
        ('LOGO', 'Logo'),
        ('SIGNATURE', 'Firma'),
        ('SEAL', 'Sello'),
        ('ICON', 'Ícono'),
    ]
    
    name = CharField(max_length=200)
    asset_type = CharField(choices=ASSET_TYPES)
    file = ImageField(upload_to='template_assets/')
    category = CharField(max_length=100)  # para organización
    is_public = BooleanField(default=True)
    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
```

#### Extended CertificateTemplate Model
```python
# Agregar campos al modelo existente:
class CertificateTemplate(models.Model):
    # ... campos existentes ...
    
    # Nuevos campos para editor visual
    canvas_width = IntegerField(default=842)  # A4 width en píxeles @72dpi
    canvas_height = IntegerField(default=595)  # A4 height landscape
    background_asset = ForeignKey(TemplateAsset, null=True)
    
    # Configuración de renderizado
    render_config = JSONField(default=dict)  # DPI, márgenes, etc.
    
    # Variables disponibles
    available_variables = JSONField(default=list)  # lista de variables
    
    # Metadatos del editor
    editor_version = CharField(max_length=20, default='1.0')
    last_edited_by = ForeignKey(User, null=True)
```

### 2. Frontend Components

#### TemplateEditor (Main Component)
```javascript
class TemplateEditor {
    constructor(canvasId, templateId) {
        this.canvas = new fabric.Canvas(canvasId);
        this.templateId = templateId;
        this.elements = [];
        this.selectedElement = null;
        this.history = new UndoRedoManager();
    }
    
    // Gestión de elementos
    addElement(type, config) { }
    removeElement(elementId) { }
    updateElement(elementId, properties) { }
    
    // Interacción
    selectElement(elementId) { }
    moveElement(elementId, x, y) { }
    resizeElement(elementId, width, height) { }
    rotateElement(elementId, angle) { }
    
    // Capas
    bringToFront(elementId) { }
    sendToBack(elementId) { }
    changeZIndex(elementId, newIndex) { }
    
    // Persistencia
    saveTemplate() { }
    loadTemplate(templateId) { }
    exportTemplate() { }
}
```

#### ElementLibrary Component
```javascript
class ElementLibrary {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.assets = [];
        this.categories = [];
    }
    
    loadAssets() { }
    filterByCategory(category) { }
    searchAssets(query) { }
    uploadNewAsset(file, type) { }
    deleteAsset(assetId) { }
}
```

#### LaTeXRenderer Component
```javascript
class LaTeXRenderer {
    constructor() {
        this.mathjax = window.MathJax;
    }
    
    renderInline(latex) { }
    renderDisplay(latex) { }
    validateSyntax(latex) { }
    convertToSVG(latex) { }
}
```

#### PreviewPanel Component
```javascript
class PreviewPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.testData = {};
    }
    
    setTestData(data) { }
    generatePreview() { }
    downloadPDF() { }
    toggleFullscreen() { }
}
```

### 3. Backend Services

#### TemplateRenderingService
```python
class TemplateRenderingService:
    """Servicio para renderizar plantillas a PDF"""
    
    def render_template(self, template_id, data):
        """Renderiza una plantilla con datos específicos"""
        template = CertificateTemplate.objects.get(id=template_id)
        elements = TemplateElement.objects.filter(template=template)
        
        # 1. Construir HTML con elementos posicionados
        html = self._build_html(template, elements, data)
        
        # 2. Procesar LaTeX a SVG
        html = self._process_latex(html)
        
        # 3. Generar PDF con WeasyPrint
        pdf = self._generate_pdf(html, template.render_config)
        
        return pdf
    
    def _build_html(self, template, elements, data):
        """Construye HTML posicionado absolutamente"""
        pass
    
    def _process_latex(self, html):
        """Convierte LaTeX a SVG usando MathJax"""
        pass
    
    def _generate_pdf(self, html, config):
        """Genera PDF final con WeasyPrint"""
        pass
```

#### TemplateExportService
```python
class TemplateExportService:
    """Servicio para exportar/importar plantillas"""
    
    def export_template(self, template_id):
        """Exporta plantilla completa a ZIP"""
        template = CertificateTemplate.objects.get(id=template_id)
        elements = TemplateElement.objects.filter(template=template)
        assets = self._get_related_assets(elements)
        
        # Crear ZIP con estructura
        zip_buffer = self._create_zip(template, elements, assets)
        return zip_buffer
    
    def import_template(self, zip_file):
        """Importa plantilla desde ZIP"""
        # Extraer y validar
        # Crear objetos en BD
        # Copiar assets
        pass
```



### 4. API Endpoints

#### Template Management
```
GET    /api/templates/                    # Listar plantillas
POST   /api/templates/                    # Crear plantilla
GET    /api/templates/{id}/               # Obtener plantilla
PUT    /api/templates/{id}/               # Actualizar plantilla
DELETE /api/templates/{id}/               # Eliminar plantilla
POST   /api/templates/{id}/duplicate/     # Duplicar plantilla
GET    /api/templates/{id}/preview/       # Vista previa con datos de prueba
POST   /api/templates/{id}/export/        # Exportar plantilla
POST   /api/templates/import/             # Importar plantilla
```

#### Element Management
```
GET    /api/templates/{id}/elements/      # Listar elementos
POST   /api/templates/{id}/elements/      # Crear elemento
PUT    /api/elements/{id}/                # Actualizar elemento
DELETE /api/elements/{id}/                # Eliminar elemento
POST   /api/elements/{id}/move/           # Mover elemento
POST   /api/elements/{id}/resize/         # Redimensionar elemento
POST   /api/elements/{id}/z-index/        # Cambiar z-index
```

#### Asset Management
```
GET    /api/assets/                       # Listar assets
POST   /api/assets/                       # Subir asset
GET    /api/assets/{id}/                  # Obtener asset
DELETE /api/assets/{id}/                  # Eliminar asset
GET    /api/assets/categories/            # Listar categorías
```

#### LaTeX Processing
```
POST   /api/latex/render/                 # Renderizar LaTeX a SVG
POST   /api/latex/validate/               # Validar sintaxis LaTeX
```

#### Variables
```
GET    /api/variables/available/          # Variables disponibles del sistema
```

## Data Models

### Element Style Configuration Schema
```json
{
  "text": {
    "fontFamily": "Arial",
    "fontSize": 24,
    "fontWeight": "normal",
    "fontStyle": "normal",
    "color": "#000000",
    "textAlign": "left",
    "lineHeight": 1.2,
    "letterSpacing": 0
  },
  "border": {
    "width": 0,
    "color": "#000000",
    "style": "solid"
  },
  "background": {
    "color": "transparent",
    "opacity": 1
  },
  "shadow": {
    "enabled": false,
    "offsetX": 0,
    "offsetY": 0,
    "blur": 0,
    "color": "#000000"
  }
}
```

### Template Render Configuration Schema
```json
{
  "page": {
    "width": 842,
    "height": 595,
    "orientation": "landscape",
    "unit": "px"
  },
  "pdf": {
    "dpi": 300,
    "quality": "high",
    "compression": true
  },
  "margins": {
    "top": 0,
    "right": 0,
    "bottom": 0,
    "left": 0
  }
}
```

### Available Variables Schema
```json
[
  {
    "key": "participant_name",
    "label": "Nombre del Participante",
    "type": "string",
    "example": "Juan Pérez García"
  },
  {
    "key": "participant_dni",
    "label": "DNI del Participante",
    "type": "string",
    "example": "12345678"
  },
  {
    "key": "event_name",
    "label": "Nombre del Evento",
    "type": "string",
    "example": "Curso de Python Avanzado"
  },
  {
    "key": "event_date",
    "label": "Fecha del Evento",
    "type": "date",
    "format": "DD/MM/YYYY",
    "example": "15/10/2024"
  },
  {
    "key": "certificate_uuid",
    "label": "UUID del Certificado",
    "type": "string",
    "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
]
```

## Error Handling

### Frontend Error Handling
```javascript
class EditorErrorHandler {
    handleError(error) {
        switch(error.type) {
            case 'NETWORK_ERROR':
                this.showNotification('Error de conexión', 'error');
                break;
            case 'VALIDATION_ERROR':
                this.showValidationErrors(error.fields);
                break;
            case 'LATEX_SYNTAX_ERROR':
                this.highlightLatexError(error.position);
                break;
            case 'FILE_SIZE_ERROR':
                this.showNotification('Archivo demasiado grande', 'error');
                break;
            default:
                this.showNotification('Error inesperado', 'error');
        }
    }
}
```

### Backend Error Responses
```python
# Estructura estándar de error
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Los datos proporcionados no son válidos",
        "details": {
            "field": "position_x",
            "reason": "Debe ser un número positivo"
        }
    }
}

# Códigos de error
ERROR_CODES = {
    'TEMPLATE_NOT_FOUND': 404,
    'ELEMENT_NOT_FOUND': 404,
    'ASSET_NOT_FOUND': 404,
    'VALIDATION_ERROR': 400,
    'LATEX_SYNTAX_ERROR': 400,
    'FILE_TOO_LARGE': 413,
    'UNSUPPORTED_FORMAT': 415,
    'PERMISSION_DENIED': 403,
    'INTERNAL_ERROR': 500,
}
```

### Error Recovery Strategies

1. **Auto-save**: Guardar automáticamente cada 30 segundos
2. **Local Storage**: Backup en localStorage del navegador
3. **Undo/Redo**: Historial de cambios para recuperación
4. **Validation**: Validación en tiempo real antes de guardar
5. **Graceful Degradation**: Funcionalidad básica si falla JavaScript



## Testing Strategy

### Unit Tests

#### Backend Tests
```python
# tests/test_template_rendering.py
class TemplateRenderingServiceTests(TestCase):
    def test_render_template_with_text_elements(self):
        """Verifica renderizado de elementos de texto"""
        pass
    
    def test_render_template_with_latex(self):
        """Verifica renderizado de fórmulas LaTeX"""
        pass
    
    def test_render_template_with_variables(self):
        """Verifica sustitución de variables"""
        pass
    
    def test_render_template_with_background(self):
        """Verifica inclusión de imagen de fondo"""
        pass

# tests/test_template_export.py
class TemplateExportServiceTests(TestCase):
    def test_export_template_creates_valid_zip(self):
        """Verifica que la exportación crea un ZIP válido"""
        pass
    
    def test_import_template_restores_all_elements(self):
        """Verifica que la importación restaura todos los elementos"""
        pass

# tests/test_latex_processing.py
class LaTeXProcessingTests(TestCase):
    def test_valid_latex_renders_correctly(self):
        """Verifica renderizado de LaTeX válido"""
        pass
    
    def test_invalid_latex_raises_error(self):
        """Verifica que LaTeX inválido genera error"""
        pass
```

#### Frontend Tests
```javascript
// tests/editor.test.js
describe('TemplateEditor', () => {
    test('should add element to canvas', () => {
        // Test agregar elemento
    });
    
    test('should update element position', () => {
        // Test mover elemento
    });
    
    test('should maintain z-index order', () => {
        // Test orden de capas
    });
    
    test('should save template correctly', () => {
        // Test guardar plantilla
    });
});

// tests/latex-renderer.test.js
describe('LaTeXRenderer', () => {
    test('should render inline latex', () => {
        // Test renderizado inline
    });
    
    test('should render display latex', () => {
        // Test renderizado display
    });
    
    test('should validate latex syntax', () => {
        // Test validación
    });
});
```

### Integration Tests

```python
# tests/test_editor_integration.py
class EditorIntegrationTests(TestCase):
    def test_complete_template_creation_workflow(self):
        """
        Test del flujo completo:
        1. Crear plantilla
        2. Agregar elementos
        3. Configurar estilos
        4. Guardar
        5. Generar preview
        6. Generar certificado final
        """
        pass
    
    def test_template_export_import_workflow(self):
        """
        Test de exportación e importación:
        1. Crear plantilla completa
        2. Exportar a ZIP
        3. Importar desde ZIP
        4. Verificar que todo se restauró correctamente
        """
        pass
```

### End-to-End Tests

```javascript
// e2e/editor.spec.js
describe('Template Editor E2E', () => {
    test('User can create a complete certificate template', async () => {
        // 1. Login como admin
        // 2. Navegar a editor
        // 3. Subir imagen de fondo
        // 4. Agregar elementos de texto
        // 5. Agregar fórmula LaTeX
        // 6. Posicionar elementos
        // 7. Guardar plantilla
        // 8. Generar preview
        // 9. Verificar PDF generado
    });
});
```

### Performance Tests

```python
# tests/test_performance.py
class PerformanceTests(TestCase):
    def test_render_template_performance(self):
        """Verifica que renderizado tome menos de 5 segundos"""
        start = time.time()
        service.render_template(template_id, data)
        duration = time.time() - start
        self.assertLess(duration, 5.0)
    
    def test_latex_rendering_performance(self):
        """Verifica que renderizado LaTeX sea eficiente"""
        pass
    
    def test_large_template_handling(self):
        """Verifica manejo de plantillas con muchos elementos"""
        pass
```

### Test Data

```python
# tests/fixtures/test_data.py
SAMPLE_TEMPLATE_DATA = {
    'name': 'Certificado de Prueba',
    'canvas_width': 842,
    'canvas_height': 595,
    'background_asset_id': 1,
}

SAMPLE_ELEMENT_DATA = {
    'element_type': 'TEXT',
    'name': 'Nombre del Participante',
    'position_x': 100,
    'position_y': 200,
    'width': 400,
    'height': 50,
    'content': '{{participant_name}}',
    'style_config': {
        'text': {
            'fontFamily': 'Arial',
            'fontSize': 24,
            'color': '#000000'
        }
    }
}

SAMPLE_LATEX_ELEMENT = {
    'element_type': 'LATEX',
    'name': 'Fórmula',
    'content': '$E = mc^2$',
    'position_x': 300,
    'position_y': 400,
}
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- Crear modelos de datos (TemplateElement, TemplateAsset)
- Implementar APIs básicas (CRUD para templates y elements)
- Setup de Fabric.js en frontend
- Implementar canvas básico con drag-and-drop

### Phase 2: Element Management (Week 3)
- Implementar biblioteca de elementos
- Sistema de upload de assets
- Posicionamiento y redimensionamiento
- Sistema de capas (z-index)

### Phase 3: Text and Variables (Week 4)
- Editor de texto con estilos
- Sistema de variables dinámicas
- Autocompletado de variables
- Preview con datos de prueba

### Phase 4: LaTeX Support (Week 5)
- Integración de MathJax
- Editor de fórmulas LaTeX
- Validación de sintaxis
- Renderizado a SVG/PDF

### Phase 5: Rendering Engine (Week 6)
- Servicio de renderizado a PDF
- Procesamiento de LaTeX en PDF
- Optimización de calidad
- Manejo de imágenes de alta resolución

### Phase 6: Import/Export (Week 7)
- Sistema de exportación a ZIP
- Sistema de importación desde ZIP
- Validación de plantillas importadas
- Migración de plantillas antiguas

### Phase 7: Polish & Testing (Week 8)
- Tests completos
- Optimización de performance
- Documentación
- Accesibilidad y responsive

## Security Considerations

### File Upload Security
```python
# Validación de archivos
ALLOWED_IMAGE_FORMATS = ['PNG', 'JPG', 'JPEG', 'SVG']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_uploaded_file(file):
    # Verificar extensión
    # Verificar tipo MIME
    # Verificar tamaño
    # Escanear contenido (si es posible)
    pass
```

### LaTeX Security
```python
# Prevenir comandos peligrosos en LaTeX
FORBIDDEN_LATEX_COMMANDS = [
    '\\input',
    '\\include',
    '\\write',
    '\\immediate',
    '\\openout',
]

def sanitize_latex(latex_code):
    for cmd in FORBIDDEN_LATEX_COMMANDS:
        if cmd in latex_code:
            raise SecurityError(f"Comando prohibido: {cmd}")
    return latex_code
```

### Access Control
```python
# Permisos para edición de plantillas
class TemplatePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Solo staff puede editar plantillas
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_staff
        return True
```

### XSS Prevention
```javascript
// Sanitizar contenido antes de renderizar
function sanitizeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}
```

## Performance Optimization

### Frontend Optimization
- Lazy loading de assets
- Debouncing de auto-save
- Virtual scrolling para lista de elementos
- Canvas rendering optimization
- Image compression antes de upload

### Backend Optimization
- Caching de plantillas renderizadas
- Async processing para PDFs grandes
- Database indexing en campos frecuentes
- CDN para assets estáticos
- Compression de respuestas API

### Database Optimization
```python
# Índices recomendados
class Meta:
    indexes = [
        models.Index(fields=['template', 'z_index']),
        models.Index(fields=['asset_type', 'category']),
        models.Index(fields=['is_public', 'created_at']),
    ]
```

## Monitoring and Logging

```python
# Logging de operaciones críticas
import logging

logger = logging.getLogger('template_editor')

def render_template(template_id, data):
    logger.info(f"Rendering template {template_id}")
    try:
        result = _do_render(template_id, data)
        logger.info(f"Template {template_id} rendered successfully")
        return result
    except Exception as e:
        logger.error(f"Error rendering template {template_id}: {str(e)}")
        raise
```

## Deployment Considerations

### Static Files
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configurar para producción con CDN
if not DEBUG:
    AWS_STORAGE_BUCKET_NAME = 'your-bucket'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### Dependencies
```
# requirements.txt adicionales
Fabric==5.3.0
MathJax==3.2.2
WeasyPrint==60.1
PyMuPDF==1.23.8
Pillow==10.1.0
```

### Environment Variables
```bash
# .env
TEMPLATE_EDITOR_MAX_FILE_SIZE=10485760
TEMPLATE_EDITOR_ALLOWED_FORMATS=PNG,JPG,JPEG,SVG
TEMPLATE_EDITOR_CACHE_TIMEOUT=3600
MATHJAX_CDN_URL=https://cdn.jsdelivr.net/npm/mathjax@3/
```
