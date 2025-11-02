"""
Servicio para renderizar plantillas visuales a PDF.
"""
import os
import tempfile
from typing import Dict, List, Optional, Any
from django.template.loader import render_to_string
from django.conf import settings
import base64
from io import BytesIO
import logging

from ..models import CertificateTemplate, TemplateElement, TemplateAsset
from .latex_validator import LaTeXValidator

# Try to import WeasyPrint, but handle gracefully if not available
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    HTML = None
    CSS = None
    FontConfiguration = None

# Try to import PIL, but handle gracefully if not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

logger = logging.getLogger(__name__)


class TemplateRenderingService:
    """
    Servicio para renderizar plantillas visuales a PDF usando WeasyPrint.
    
    Convierte el diseño visual del editor en HTML posicionado absolutamente
    y luego genera un PDF de alta calidad.
    """
    
    def __init__(self):
        self.latex_validator = LaTeXValidator()
        self.font_config = FontConfiguration() if WEASYPRINT_AVAILABLE else None
    
    def render_template_to_pdf(
        self, 
        template_id: int, 
        participant_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Renderiza una plantilla completa a PDF.
        
        Args:
            template_id: ID de la plantilla a renderizar
            participant_data: Datos del participante para variables
            output_path: Ruta opcional donde guardar el PDF
            
        Returns:
            Bytes del PDF generado
        """
        try:
            # Cargar plantilla y elementos
            template = CertificateTemplate.objects.get(id=template_id)
            elements = TemplateElement.objects.filter(
                template=template,
                is_visible=True
            ).order_by('z_index')
            
            # Construir HTML
            html_content = self._build_html(template, elements, participant_data)
            
            # Generar PDF
            pdf_bytes = self._generate_pdf(html_content, template)
            
            # Guardar si se especifica ruta
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
            
            logger.info(f"Template {template_id} rendered successfully")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error rendering template {template_id}: {str(e)}")
            raise
    
    def _build_html(
        self, 
        template: CertificateTemplate, 
        elements: List[TemplateElement], 
        data: Dict[str, Any]
    ) -> str:
        """
        Construye el HTML con elementos posicionados absolutamente.
        
        Args:
            template: Plantilla base
            elements: Lista de elementos a renderizar
            data: Datos para reemplazar variables
            
        Returns:
            HTML completo listo para PDF
        """
        # Procesar elementos
        processed_elements = []
        for element in elements:
            processed_element = self._process_element(element, data)
            if processed_element:
                processed_elements.append(processed_element)
        
        # Obtener imagen de fondo si existe
        background_url = None
        if template.background_asset:
            background_url = self._get_asset_data_url(template.background_asset)
        elif template.background_image:
            background_url = template.background_image.url
        
        # Configuración de renderizado
        render_config = template.render_config or {}
        page_config = render_config.get('page', {})
        
        canvas_width = template.canvas_width
        canvas_height = template.canvas_height
        
        # Contexto para el template
        context = {
            'template': template,
            'elements': processed_elements,
            'background_url': background_url,
            'canvas_width': canvas_width,
            'canvas_height': canvas_height,
            'page_config': page_config,
            'participant_data': data
        }
        
        # Renderizar template HTML
        html_content = render_to_string('certificates/pdf_template.html', context)
        
        return html_content
    
    def _process_element(
        self, 
        element: TemplateElement, 
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Procesa un elemento individual para renderizado.
        
        Args:
            element: Elemento a procesar
            data: Datos para variables
            
        Returns:
            Diccionario con datos del elemento procesado
        """
        try:
            processed = {
                'id': element.id,
                'type': element.element_type,
                'name': element.name,
                'position_x': element.position_x,
                'position_y': element.position_y,
                'width': element.width,
                'height': element.height,
                'rotation': element.rotation,
                'z_index': element.z_index,
                'style_config': element.style_config or {},
                'content': element.content,
                'processed_content': None,
                'asset_url': None,
                'css_styles': {}
            }
            
            # Procesar según tipo de elemento
            if element.element_type in ['TEXT', 'VARIABLE']:
                processed['processed_content'] = self._process_text_content(
                    element.content, data
                )
                processed['css_styles'] = self._build_text_styles(element.style_config)
                
            elif element.element_type == 'LATEX':
                processed['processed_content'] = self._process_latex_content(
                    element.content
                )
                processed['css_styles'] = self._build_latex_styles(element.style_config)
                
            elif element.element_type == 'IMAGE':
                if element.asset:
                    processed['asset_url'] = self._get_asset_data_url(element.asset)
                processed['css_styles'] = self._build_image_styles(element.style_config)
                
            elif element.element_type == 'QR':
                # Generar QR code
                qr_data = self._generate_qr_data(data)
                processed['qr_data'] = qr_data
                processed['css_styles'] = self._build_qr_styles(element.style_config)
            
            # Estilos de posicionamiento comunes
            processed['css_styles'].update({
                'position': 'absolute',
                'left': f'{element.position_x}px',
                'top': f'{element.position_y}px',
                'width': f'{element.width}px',
                'height': f'{element.height}px',
                'z-index': str(element.z_index),
                'transform': f'rotate({element.rotation}deg)' if element.rotation else 'none'
            })
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing element {element.id}: {str(e)}")
            return None
    
    def _process_text_content(self, content: str, data: Dict[str, Any]) -> str:
        """
        Procesa contenido de texto reemplazando variables.
        
        Args:
            content: Contenido original
            data: Datos para reemplazar variables
            
        Returns:
            Contenido con variables reemplazadas
        """
        processed_content = content
        
        # Reemplazar variables {{variable_name}}
        import re
        variable_pattern = r'\{\{([^}]+)\}\}'
        
        def replace_variable(match):
            var_name = match.group(1).strip()
            return str(data.get(var_name, f'{{{{ {var_name} }}}}'))
        
        processed_content = re.sub(variable_pattern, replace_variable, processed_content)
        
        return processed_content
    
    def _process_latex_content(self, latex_code: str) -> str:
        """
        Procesa contenido LaTeX.
        
        Args:
            latex_code: Código LaTeX
            
        Returns:
            HTML renderizado o código LaTeX sanitizado
        """
        # Validar LaTeX
        validation_result = self.latex_validator.validate_latex(latex_code)
        
        if not validation_result['is_valid']:
            logger.warning(f"Invalid LaTeX code: {latex_code}")
            return f"[LaTeX Error: {validation_result['errors'][0]}]"
        
        # Por ahora, retornar el código sanitizado
        # En una implementación completa, aquí se renderizaría con MathJax
        sanitized_code = validation_result['sanitized_code']
        
        # Formatear para display
        if sanitized_code.startswith('$$') and sanitized_code.endswith('$$'):
            return f'<div class="latex-display">{sanitized_code}</div>'
        elif sanitized_code.startswith('$') and sanitized_code.endswith('$'):
            return f'<span class="latex-inline">{sanitized_code}</span>'
        else:
            return f'<span class="latex-inline">${sanitized_code}$</span>'
    
    def _generate_qr_data(self, data: Dict[str, Any]) -> str:
        """
        Genera datos para código QR.
        
        Args:
            data: Datos del participante
            
        Returns:
            URL o datos para el QR
        """
        # Por ahora, generar URL de verificación simple
        certificate_uuid = data.get('certificate_uuid', 'unknown')
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/certificado/{certificate_uuid}/preview/"
    
    def _get_asset_data_url(self, asset: TemplateAsset) -> str:
        """
        Convierte un asset a data URL para embebido en PDF.
        
        Args:
            asset: Asset a convertir
            
        Returns:
            Data URL del asset
        """
        try:
            with asset.file.open('rb') as f:
                file_content = f.read()
            
            # Detectar tipo MIME
            file_extension = asset.file.name.lower().split('.')[-1]
            mime_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'svg': 'image/svg+xml'
            }
            
            mime_type = mime_types.get(file_extension, 'image/png')
            
            # Convertir a base64
            base64_content = base64.b64encode(file_content).decode('utf-8')
            
            return f"data:{mime_type};base64,{base64_content}"
            
        except Exception as e:
            logger.error(f"Error converting asset {asset.id} to data URL: {str(e)}")
            return ""
    
    def _build_text_styles(self, style_config: Dict[str, Any]) -> Dict[str, str]:
        """Construye estilos CSS para elementos de texto"""
        styles = {}
        
        text_config = style_config.get('text', {})
        
        if 'fontFamily' in text_config:
            styles['font-family'] = text_config['fontFamily']
        
        if 'fontSize' in text_config:
            styles['font-size'] = f"{text_config['fontSize']}px"
        
        if 'color' in text_config:
            styles['color'] = text_config['color']
        
        if 'textAlign' in text_config:
            styles['text-align'] = text_config['textAlign']
        
        if 'fontWeight' in text_config:
            styles['font-weight'] = text_config['fontWeight']
        
        if 'fontStyle' in text_config:
            styles['font-style'] = text_config['fontStyle']
        
        if 'lineHeight' in text_config:
            styles['line-height'] = str(text_config['lineHeight'])
        
        if 'letterSpacing' in text_config:
            styles['letter-spacing'] = f"{text_config['letterSpacing']}px"
        
        # Estilos de borde
        border_config = style_config.get('border', {})
        if border_config.get('width', 0) > 0:
            styles['border'] = f"{border_config['width']}px {border_config.get('style', 'solid')} {border_config.get('color', '#000000')}"
        
        # Estilos de fondo
        bg_config = style_config.get('background', {})
        if bg_config.get('color') and bg_config['color'] != 'transparent':
            styles['background-color'] = bg_config['color']
        
        if 'opacity' in bg_config:
            styles['opacity'] = str(bg_config['opacity'])
        
        # Sombra
        shadow_config = style_config.get('shadow', {})
        if shadow_config.get('enabled'):
            shadow_parts = [
                f"{shadow_config.get('offsetX', 0)}px",
                f"{shadow_config.get('offsetY', 0)}px",
                f"{shadow_config.get('blur', 0)}px",
                shadow_config.get('color', '#000000')
            ]
            styles['text-shadow'] = ' '.join(shadow_parts)
        
        return styles
    
    def _build_latex_styles(self, style_config: Dict[str, Any]) -> Dict[str, str]:
        """Construye estilos CSS para elementos LaTeX"""
        styles = self._build_text_styles(style_config)
        
        # Estilos específicos para LaTeX
        styles.update({
            'font-family': 'Times New Roman, serif',
            'text-align': 'center'
        })
        
        return styles
    
    def _build_image_styles(self, style_config: Dict[str, Any]) -> Dict[str, str]:
        """Construye estilos CSS para elementos de imagen"""
        styles = {
            'object-fit': 'contain',
            'max-width': '100%',
            'max-height': '100%'
        }
        
        # Estilos de borde para imágenes
        border_config = style_config.get('border', {})
        if border_config.get('width', 0) > 0:
            styles['border'] = f"{border_config['width']}px {border_config.get('style', 'solid')} {border_config.get('color', '#000000')}"
        
        # Opacidad
        bg_config = style_config.get('background', {})
        if 'opacity' in bg_config:
            styles['opacity'] = str(bg_config['opacity'])
        
        return styles
    
    def _build_qr_styles(self, style_config: Dict[str, Any]) -> Dict[str, str]:
        """Construye estilos CSS para elementos QR"""
        styles = {
            'display': 'flex',
            'justify-content': 'center',
            'align-items': 'center',
            'background-color': '#ffffff',
            'border': '1px solid #cccccc'
        }
        
        return styles
    
    def _generate_pdf(self, html_content: str, template: CertificateTemplate) -> bytes:
        """
        Genera PDF desde HTML usando WeasyPrint.
        
        Args:
            html_content: HTML a convertir
            template: Plantilla con configuración
            
        Returns:
            Bytes del PDF generado
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint is not available. Please install it with: "
                "pip install weasyprint"
            )
        
        try:
            # Configuración de renderizado
            render_config = template.render_config or {}
            pdf_config = render_config.get('pdf', {})
            
            # CSS base para PDF
            base_css = self._get_base_css(template)
            
            # Crear objeto HTML
            html_doc = HTML(string=html_content, base_url=settings.MEDIA_URL)
            
            # Crear CSS
            css_doc = CSS(string=base_css, font_config=self.font_config)
            
            # Generar PDF
            pdf_bytes = html_doc.write_pdf(
                stylesheets=[css_doc],
                font_config=self.font_config,
                optimize_images=True,
                presentational_hints=True
            )
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _get_base_css(self, template: CertificateTemplate) -> str:
        """
        Genera CSS base para el PDF con soporte para A4 vertical y horizontal.
        
        Args:
            template: Plantilla con configuración
            
        Returns:
            CSS como string
        """
        render_config = template.render_config or {}
        page_config = render_config.get('page', {})
        
        # Dimensiones de página
        page_width = page_config.get('width', template.canvas_width)
        page_height = page_config.get('height', template.canvas_height)
        
        # Detectar orientación
        is_landscape = page_width > page_height
        orientation = 'landscape' if is_landscape else 'portrait'
        
        # Configurar tamaño de página CSS
        if (page_width, page_height) == (842, 595):
            page_size = "A4 landscape"
        elif (page_width, page_height) == (595, 842):
            page_size = "A4 portrait"
        elif (page_width, page_height) == (792, 612):
            page_size = "letter landscape"
        elif (page_width, page_height) == (612, 792):
            page_size = "letter portrait"
        else:
            page_size = f"{page_width}px {page_height}px"
        
        css = f"""
        @page {{
            size: {page_size};
            margin: 0;
            padding: 0;
            orientation: {orientation};
        }}
        
        body {{
            margin: 0;
            padding: 0;
            width: {page_width}px;
            height: {page_height}px;
            font-family: Arial, sans-serif;
            position: relative;
            overflow: hidden;
            box-sizing: border-box;
        }}
        
        .certificate-container {{
            position: relative;
            width: 100%;
            height: 100%;
            box-sizing: border-box;
        }}
        
        .background-image {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            object-fit: cover;
        }}
        
        .element {{
            position: absolute;
            box-sizing: border-box;
        }}
        
        .element-text {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            word-wrap: break-word;
            overflow: hidden;
            line-height: 1.2;
        }}
        
        .element-image {{
            display: block;
            object-fit: contain;
        }}
        
        .element-qr {{
            display: flex;
            justify-content: center;
            align-items: center;
            background: white;
            border: 1px solid #ccc;
        }}
        
        .element-latex {{
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Times New Roman', serif;
        }}
        
        .latex-display {{
            text-align: center;
            font-size: 18px;
        }}
        
        .latex-inline {{
            font-size: 16px;
        }}
        
        /* Fuentes optimizadas para impresión */
        @font-face {{
            font-family: 'Times New Roman';
            src: local('Times New Roman'), local('TimesNewRoman');
        }}
        
        @font-face {{
            font-family: 'Arial';
            src: local('Arial'), local('ArialMT');
        }}
        
        @font-face {{
            font-family: 'Helvetica';
            src: local('Helvetica'), local('Helvetica Neue');
        }}
        
        @font-face {{
            font-family: 'Georgia';
            src: local('Georgia'), local('Georgia-Regular');
        }}
        
        /* Estilos específicos para orientación */
        .landscape-layout {{
            width: {page_width}px;
            height: {page_height}px;
        }}
        
        .portrait-layout {{
            width: {page_width}px;
            height: {page_height}px;
        }}
        
        /* Optimizaciones para impresión */
        @media print {{
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            .element {{
                page-break-inside: avoid;
            }}
        }}
        """
        
        return css
    
    def generate_preview_image(
        self, 
        template_id: int, 
        participant_data: Dict[str, Any],
        format: str = 'PNG',
        width: int = 800
    ) -> bytes:
        """
        Genera una imagen de vista previa de la plantilla.
        
        Args:
            template_id: ID de la plantilla
            participant_data: Datos del participante
            format: Formato de imagen (PNG, JPEG)
            width: Ancho de la imagen
            
        Returns:
            Bytes de la imagen generada
        """
        if not PIL_AVAILABLE:
            raise ImportError(
                "PIL (Pillow) is not available. Please install it with: "
                "pip install Pillow"
            )
        
        try:
            # Generar PDF primero
            pdf_bytes = self.render_template_to_pdf(template_id, participant_data)
            
            # Convertir primera página del PDF a imagen
            # Nota: Esto requeriría una biblioteca como pdf2image
            # Por ahora, retornar placeholder
            
            # Crear imagen placeholder
            template = CertificateTemplate.objects.get(id=template_id)
            aspect_ratio = template.canvas_height / template.canvas_width
            height = int(width * aspect_ratio)
            
            # Crear imagen simple
            img = Image.new('RGB', (width, height), color='white')
            
            # Convertir a bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format=format)
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating preview image: {str(e)}")
            raise


# Función de utilidad para renderizado rápido
def render_certificate_pdf(template_id: int, participant_data: Dict[str, Any]) -> bytes:
    """
    Función de utilidad para renderizar un certificado a PDF.
    
    Args:
        template_id: ID de la plantilla
        participant_data: Datos del participante
        
    Returns:
        Bytes del PDF generado
    """
    renderer = TemplateRenderingService()
    return renderer.render_template_to_pdf(template_id, participant_data)


# Función para generar datos de prueba
def get_sample_participant_data() -> Dict[str, Any]:
    """
    Genera datos de prueba para renderizado.
    
    Returns:
        Diccionario con datos de ejemplo
    """
    return {
        'participant_name': 'Juan Pérez García',
        'participant_dni': '12345678',
        'event_name': 'Curso de Ejemplo Avanzado',
        'event_date': '15/11/2024',
        'certificate_uuid': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'attendee_type': 'Asistente',
        'event_hours': '40',
        'event_location': 'Lima, Perú',
        'issue_date': '20/11/2024'
    }