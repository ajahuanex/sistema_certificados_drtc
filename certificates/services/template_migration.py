"""
Servicio para migrar plantillas HTML existentes al formato visual.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from django.db import transaction

# Try to import BeautifulSoup, but handle gracefully if not available
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

from ..models import CertificateTemplate, TemplateElement, TemplateAsset

logger = logging.getLogger(__name__)


class TemplateMigrationService:
    """
    Servicio para migrar plantillas HTML existentes al nuevo formato visual.
    
    Analiza el HTML y CSS de plantillas existentes e intenta crear elementos
    visuales equivalentes en el editor.
    """
    
    def __init__(self):
        # Tamaños estándar A4 a 72 DPI
        self.A4_HORIZONTAL = (842, 595)  # A4 landscape
        self.A4_VERTICAL = (595, 842)    # A4 portrait
        self.default_canvas_width = 842   # Por defecto horizontal para certificados
        self.default_canvas_height = 595
    
    def migrate_template(self, template_id: int, preserve_original: bool = True) -> Dict:
        """
        Migra una plantilla HTML al formato visual.
        
        Args:
            template_id: ID de la plantilla a migrar
            preserve_original: Si mantener el HTML original como respaldo
            
        Returns:
            Diccionario con resultado de la migración
        """
        if not BS4_AVAILABLE:
            return {
                'success': False,
                'error': 'BeautifulSoup4 is required for template migration. Install with: pip install beautifulsoup4'
            }
        
        try:
            template = CertificateTemplate.objects.get(id=template_id)
            
            # Verificar si ya tiene elementos visuales
            if template.elements.exists():
                return {
                    'success': False,
                    'error': 'La plantilla ya tiene elementos visuales',
                    'elements_count': template.elements.count()
                }
            
            with transaction.atomic():
                # Analizar HTML y crear elementos
                elements_created = self._analyze_and_create_elements(template)
                
                # Actualizar configuración de la plantilla
                self._update_template_config(template)
                
                # Preservar HTML original si se solicita
                if preserve_original and template.html_template:
                    # Crear un comentario con el HTML original
                    original_html = f"<!-- HTML ORIGINAL ANTES DE MIGRACIÓN:\n{template.html_template}\n-->"
                    template.html_template = original_html + "\n<!-- Plantilla migrada al editor visual -->"
                
                template.editor_version = '1.0'
                template.save()
                
                logger.info(f"Template {template_id} migrated successfully with {len(elements_created)} elements")
                
                return {
                    'success': True,
                    'elements_created': len(elements_created),
                    'elements': [
                        {
                            'name': elem.name,
                            'type': elem.element_type,
                            'position': f"({elem.position_x}, {elem.position_y})",
                            'size': f"{elem.width}x{elem.height}"
                        }
                        for elem in elements_created
                    ],
                    'message': f'Plantilla migrada exitosamente con {len(elements_created)} elementos'
                }
                
        except CertificateTemplate.DoesNotExist:
            return {
                'success': False,
                'error': 'Plantilla no encontrada'
            }
        except Exception as e:
            logger.error(f"Error migrating template {template_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Error durante la migración: {str(e)}'
            }
    
    def _analyze_and_create_elements(self, template: CertificateTemplate) -> List[TemplateElement]:
        """
        Analiza el HTML de la plantilla y crea elementos visuales.
        
        Args:
            template: Plantilla a analizar
            
        Returns:
            Lista de elementos creados
        """
        elements_created = []
        
        if not template.html_template:
            return elements_created
        
        # Parsear HTML
        soup = BeautifulSoup(template.html_template, 'html.parser')
        
        # Buscar elementos con variables Django
        variable_elements = self._find_variable_elements(soup)
        elements_created.extend(variable_elements)
        
        # Buscar elementos de texto estático
        text_elements = self._find_text_elements(soup)
        elements_created.extend(text_elements)
        
        # Buscar imágenes
        image_elements = self._find_image_elements(soup)
        elements_created.extend(image_elements)
        
        # Crear elementos con la plantilla asociada
        for element_data in elements_created:
            element_data['template'] = template
        
        # Crear elementos en la base de datos
        created_elements = []
        for i, element_data in enumerate(elements_created):
            element = TemplateElement.objects.create(
                template=template,
                element_type=element_data.get('element_type', 'TEXT'),
                name=element_data.get('name', f'Elemento {i+1}'),
                position_x=element_data.get('position_x', 50 + (i * 20)),
                position_y=element_data.get('position_y', 50 + (i * 30)),
                width=element_data.get('width', 300),
                height=element_data.get('height', 50),
                rotation=element_data.get('rotation', 0),
                z_index=element_data.get('z_index', i),
                content=element_data.get('content', ''),
                variables=element_data.get('variables', {}),
                style_config=element_data.get('style_config', {}),
                is_locked=False,
                is_visible=True
            )
            created_elements.append(element)
        
        return created_elements
    
    def _find_variable_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Busca elementos que contienen variables Django.
        
        Args:
            soup: Objeto BeautifulSoup del HTML
            
        Returns:
            Lista de datos de elementos encontrados
        """
        elements = []
        
        # Patrones de variables Django
        variable_patterns = [
            r'\{\{\s*(\w+)\s*\}\}',  # {{ variable }}
            r'\{\{\s*(\w+\.\w+)\s*\}\}',  # {{ object.field }}
        ]
        
        # Buscar en todo el texto
        text_content = soup.get_text()
        
        for pattern in variable_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                variable_name = match.group(1)
                
                # Mapear variables conocidas
                mapped_content = self._map_variable_name(variable_name)
                
                elements.append({
                    'element_type': 'VARIABLE',
                    'name': f'Variable: {variable_name}',
                    'content': mapped_content,
                    'variables': {variable_name: mapped_content},
                    'style_config': {
                        'text': {
                            'fontFamily': 'Arial',
                            'fontSize': 16,
                            'color': '#000000',
                            'textAlign': 'left'
                        }
                    }
                })
        
        return elements
    
    def _find_text_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Busca elementos de texto estático.
        
        Args:
            soup: Objeto BeautifulSoup del HTML
            
        Returns:
            Lista de datos de elementos encontrados
        """
        elements = []
        
        # Buscar elementos de texto comunes
        text_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'div']
        
        for tag_name in text_tags:
            tags = soup.find_all(tag_name)
            for tag in tags:
                text_content = tag.get_text(strip=True)
                
                # Ignorar elementos vacíos o que solo contienen variables
                if not text_content or re.match(r'^\{\{.*\}\}$', text_content):
                    continue
                
                # Determinar estilo basado en el tag
                style_config = self._get_style_from_tag(tag, tag_name)
                
                elements.append({
                    'element_type': 'TEXT',
                    'name': f'Texto: {text_content[:30]}...' if len(text_content) > 30 else f'Texto: {text_content}',
                    'content': text_content,
                    'style_config': style_config
                })
        
        return elements
    
    def _find_image_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Busca elementos de imagen.
        
        Args:
            soup: Objeto BeautifulSoup del HTML
            
        Returns:
            Lista de datos de elementos encontrados
        """
        elements = []
        
        # Buscar tags img
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src', '')
            alt = img.get('alt', 'Imagen')
            
            elements.append({
                'element_type': 'IMAGE',
                'name': f'Imagen: {alt}',
                'content': src,
                'style_config': {
                    'border': {
                        'width': 0,
                        'color': '#000000',
                        'style': 'solid'
                    }
                }
            })
        
        return elements
    
    def _map_variable_name(self, variable_name: str) -> str:
        """
        Mapea nombres de variables Django a variables del sistema.
        
        Args:
            variable_name: Nombre de la variable original
            
        Returns:
            Variable mapeada para el sistema visual
        """
        mapping = {
            'full_name': '{{participant_name}}',
            'participant.full_name': '{{participant_name}}',
            'dni': '{{participant_dni}}',
            'participant.dni': '{{participant_dni}}',
            'event_name': '{{event_name}}',
            'event.name': '{{event_name}}',
            'event_date': '{{event_date}}',
            'event.event_date': '{{event_date}}',
            'attendee_type': '{{attendee_type}}',
            'participant.attendee_type': '{{attendee_type}}',
            'certificate_uuid': '{{certificate_uuid}}',
            'verification_url': '{{verification_url}}'
        }
        
        return mapping.get(variable_name, f'{{{{{variable_name}}}}}')
    
    def _get_style_from_tag(self, tag, tag_name: str) -> Dict:
        """
        Extrae estilos de un tag HTML.
        
        Args:
            tag: Tag de BeautifulSoup
            tag_name: Nombre del tag
            
        Returns:
            Configuración de estilo
        """
        style_config = {
            'text': {
                'fontFamily': 'Arial',
                'fontSize': 16,
                'color': '#000000',
                'textAlign': 'left',
                'fontWeight': 'normal',
                'fontStyle': 'normal'
            }
        }
        
        # Estilos por defecto según el tag
        if tag_name in ['h1']:
            style_config['text'].update({
                'fontSize': 32,
                'fontWeight': 'bold',
                'textAlign': 'center'
            })
        elif tag_name in ['h2']:
            style_config['text'].update({
                'fontSize': 24,
                'fontWeight': 'bold'
            })
        elif tag_name in ['h3']:
            style_config['text'].update({
                'fontSize': 20,
                'fontWeight': 'bold'
            })
        elif tag_name in ['h4', 'h5', 'h6']:
            style_config['text'].update({
                'fontSize': 18,
                'fontWeight': 'bold'
            })
        
        # Intentar extraer estilos inline
        style_attr = tag.get('style', '')
        if style_attr:
            inline_styles = self._parse_inline_styles(style_attr)
            style_config['text'].update(inline_styles)
        
        return style_config
    
    def _parse_inline_styles(self, style_str: str) -> Dict:
        """
        Parsea estilos CSS inline.
        
        Args:
            style_str: String con estilos CSS
            
        Returns:
            Diccionario con estilos parseados
        """
        styles = {}
        
        # Dividir por punto y coma
        declarations = style_str.split(';')
        
        for declaration in declarations:
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                
                # Mapear propiedades CSS conocidas
                if prop == 'font-size':
                    # Extraer número de píxeles
                    size_match = re.search(r'(\d+)', value)
                    if size_match:
                        styles['fontSize'] = int(size_match.group(1))
                
                elif prop == 'color':
                    styles['color'] = value
                
                elif prop == 'text-align':
                    styles['textAlign'] = value
                
                elif prop == 'font-weight':
                    styles['fontWeight'] = value
                
                elif prop == 'font-style':
                    styles['fontStyle'] = value
                
                elif prop == 'font-family':
                    styles['fontFamily'] = value.replace('"', '').replace("'", '')
        
        return styles
    
    def _update_template_config(self, template: CertificateTemplate):
        """
        Actualiza la configuración de la plantilla para el editor visual.
        
        Args:
            template: Plantilla a actualizar
        """
        # Configurar dimensiones del canvas si no están establecidas
        if not template.canvas_width:
            template.canvas_width = self.default_canvas_width
        
        if not template.canvas_height:
            template.canvas_height = self.default_canvas_height
        
        # Configurar variables disponibles si no están establecidas
        if not template.available_variables:
            template.available_variables = [
                'participant_name',
                'participant_dni',
                'event_name',
                'event_date',
                'attendee_type',
                'certificate_uuid',
                'verification_url'
            ]
        
        # Configurar renderizado si no está establecido
        if not template.render_config:
            template.render_config = {
                'page': {
                    'width': template.canvas_width,
                    'height': template.canvas_height,
                    'orientation': 'landscape',
                    'unit': 'px'
                },
                'pdf': {
                    'dpi': 300,
                    'quality': 'high',
                    'compression': True
                },
                'margins': {
                    'top': 0,
                    'right': 0,
                    'bottom': 0,
                    'left': 0
                }
            }
    
    def migrate_all_templates(self, exclude_with_elements: bool = True) -> Dict:
        """
        Migra todas las plantillas HTML al formato visual.
        
        Args:
            exclude_with_elements: Si excluir plantillas que ya tienen elementos
            
        Returns:
            Diccionario con resultado de la migración masiva
        """
        templates = CertificateTemplate.objects.all()
        
        if exclude_with_elements:
            # Excluir plantillas que ya tienen elementos
            templates = templates.filter(elements__isnull=True).distinct()
        
        results = {
            'total_templates': templates.count(),
            'migrated_successfully': 0,
            'migration_errors': 0,
            'results': [],
            'errors': []
        }
        
        for template in templates:
            result = self.migrate_template(template.id, preserve_original=True)
            
            if result['success']:
                results['migrated_successfully'] += 1
            else:
                results['migration_errors'] += 1
                results['errors'].append({
                    'template_id': template.id,
                    'template_name': template.name,
                    'error': result['error']
                })
            
            results['results'].append({
                'template_id': template.id,
                'template_name': template.name,
                'success': result['success'],
                'elements_created': result.get('elements_created', 0)
            })
        
        logger.info(f"Mass migration completed: {results['migrated_successfully']} success, {results['migration_errors']} errors")
        
        return results
    
    def preview_migration(self, template_id: int) -> Dict:
        """
        Previsualiza qué elementos se crearían al migrar una plantilla.
        
        Args:
            template_id: ID de la plantilla a previsualizar
            
        Returns:
            Diccionario con preview de la migración
        """
        try:
            template = CertificateTemplate.objects.get(id=template_id)
            
            if not template.html_template:
                return {
                    'success': False,
                    'error': 'La plantilla no tiene contenido HTML'
                }
            
            # Analizar sin crear elementos
            soup = BeautifulSoup(template.html_template, 'html.parser')
            
            variable_elements = self._find_variable_elements(soup)
            text_elements = self._find_text_elements(soup)
            image_elements = self._find_image_elements(soup)
            
            all_elements = variable_elements + text_elements + image_elements
            
            return {
                'success': True,
                'template_name': template.name,
                'total_elements': len(all_elements),
                'elements_by_type': {
                    'variables': len(variable_elements),
                    'text': len(text_elements),
                    'images': len(image_elements)
                },
                'elements_preview': [
                    {
                        'type': elem.get('element_type'),
                        'name': elem.get('name'),
                        'content': elem.get('content', '')[:100] + ('...' if len(elem.get('content', '')) > 100 else '')
                    }
                    for elem in all_elements[:10]  # Mostrar solo los primeros 10
                ],
                'message': f'Se crearían {len(all_elements)} elementos visuales'
            }
            
        except CertificateTemplate.DoesNotExist:
            return {
                'success': False,
                'error': 'Plantilla no encontrada'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en preview: {str(e)}'
            }


# Función de utilidad para migración rápida
def migrate_template_to_visual(template_id: int) -> Dict:
    """
    Función de utilidad para migrar una plantilla al formato visual.
    
    Args:
        template_id: ID de la plantilla a migrar
        
    Returns:
        Resultado de la migración
    """
    service = TemplateMigrationService()
    return service.migrate_template(template_id)