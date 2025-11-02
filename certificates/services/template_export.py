"""
Servicio para exportar e importar plantillas completas.
"""
import json
import zipfile
import tempfile
import os
from typing import Dict, List, Any, Optional
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
import logging

from ..models import CertificateTemplate, TemplateElement, TemplateAsset

logger = logging.getLogger(__name__)


class TemplateExportService:
    """
    Servicio para exportar e importar plantillas completas con todos sus recursos.
    
    Genera archivos ZIP que contienen:
    - template.json: Configuración de la plantilla
    - elements.json: Lista de elementos
    - assets/: Carpeta con todos los assets utilizados
    """
    
    def __init__(self):
        self.export_version = "1.0"
    
    def export_template(self, template_id: int) -> bytes:
        """
        Exporta una plantilla completa a un archivo ZIP.
        
        Args:
            template_id: ID de la plantilla a exportar
            
        Returns:
            Bytes del archivo ZIP generado
        """
        try:
            # Cargar plantilla y elementos
            template = CertificateTemplate.objects.get(id=template_id)
            elements = TemplateElement.objects.filter(template=template)
            
            # Obtener assets relacionados
            related_assets = self._get_related_assets(template, elements)
            
            # Crear ZIP en memoria
            zip_buffer = self._create_export_zip(template, elements, related_assets)
            
            logger.info(f"Template {template_id} exported successfully")
            return zip_buffer
            
        except Exception as e:
            logger.error(f"Error exporting template {template_id}: {str(e)}")
            raise
    
    def import_template(
        self, 
        zip_file_content: bytes, 
        new_name: Optional[str] = None,
        overwrite_assets: bool = False
    ) -> CertificateTemplate:
        """
        Importa una plantilla desde un archivo ZIP.
        
        Args:
            zip_file_content: Contenido del archivo ZIP
            new_name: Nombre opcional para la nueva plantilla
            overwrite_assets: Si sobrescribir assets existentes
            
        Returns:
            Plantilla importada
        """
        try:
            with transaction.atomic():
                # Extraer y validar ZIP
                extracted_data = self._extract_and_validate_zip(zip_file_content)
                
                # Importar assets primero
                asset_mapping = self._import_assets(
                    extracted_data['assets'], 
                    overwrite_assets
                )
                
                # Crear plantilla
                template = self._create_template_from_data(
                    extracted_data['template'],
                    asset_mapping,
                    new_name
                )
                
                # Crear elementos
                self._create_elements_from_data(
                    extracted_data['elements'],
                    template,
                    asset_mapping
                )
                
                logger.info(f"Template imported successfully as ID {template.id}")
                return template
                
        except Exception as e:
            logger.error(f"Error importing template: {str(e)}")
            raise
    
    def _get_related_assets(
        self, 
        template: CertificateTemplate, 
        elements: List[TemplateElement]
    ) -> List[TemplateAsset]:
        """
        Obtiene todos los assets relacionados con la plantilla.
        
        Args:
            template: Plantilla base
            elements: Lista de elementos
            
        Returns:
            Lista de assets únicos
        """
        assets = set()
        
        # Asset de fondo de la plantilla
        if template.background_asset:
            assets.add(template.background_asset)
        
        # Assets de elementos
        for element in elements:
            if element.asset:
                assets.add(element.asset)
        
        return list(assets)
    
    def _create_export_zip(
        self,
        template: CertificateTemplate,
        elements: List[TemplateElement],
        assets: List[TemplateAsset]
    ) -> bytes:
        """
        Crea el archivo ZIP de exportación.
        
        Args:
            template: Plantilla a exportar
            elements: Elementos de la plantilla
            assets: Assets relacionados
            
        Returns:
            Bytes del ZIP
        """
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile() as temp_file:
            with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                # Agregar metadatos de exportación
                export_info = {
                    'export_version': self.export_version,
                    'exported_at': template.updated_at.isoformat(),
                    'template_id': template.id,
                    'template_name': template.name,
                    'elements_count': len(elements),
                    'assets_count': len(assets)
                }
                
                zip_file.writestr(
                    'export_info.json',
                    json.dumps(export_info, indent=2, ensure_ascii=False)
                )
                
                # Agregar configuración de plantilla
                template_data = self._serialize_template(template)
                zip_file.writestr(
                    'template.json',
                    json.dumps(template_data, indent=2, ensure_ascii=False)
                )
                
                # Agregar elementos
                elements_data = [self._serialize_element(element) for element in elements]
                zip_file.writestr(
                    'elements.json',
                    json.dumps(elements_data, indent=2, ensure_ascii=False)
                )
                
                # Agregar assets
                assets_data = []
                for asset in assets:
                    asset_data = self._serialize_asset(asset)
                    assets_data.append(asset_data)
                    
                    # Agregar archivo del asset
                    try:
                        with asset.file.open('rb') as asset_file:
                            zip_file.writestr(
                                f"assets/{asset_data['filename']}",
                                asset_file.read()
                            )
                    except Exception as e:
                        logger.warning(f"Could not include asset {asset.id}: {str(e)}")
                
                zip_file.writestr(
                    'assets.json',
                    json.dumps(assets_data, indent=2, ensure_ascii=False)
                )
                
                # Agregar README
                readme_content = self._generate_readme(template, elements, assets)
                zip_file.writestr('README.txt', readme_content)
            
            # Leer contenido del archivo temporal
            temp_file.seek(0)
            return temp_file.read()
    
    def _serialize_template(self, template: CertificateTemplate) -> Dict[str, Any]:
        """Serializa una plantilla para exportación"""
        return {
            'name': template.name,
            'canvas_width': template.canvas_width,
            'canvas_height': template.canvas_height,
            'render_config': template.render_config,
            'available_variables': template.available_variables,
            'editor_version': template.editor_version,
            'background_asset_ref': template.background_asset.id if template.background_asset else None,
            
            # Campos legacy para compatibilidad
            'html_template': template.html_template,
            'css_styles': template.css_styles,
            'field_positions': template.field_positions,
        }
    
    def _serialize_element(self, element: TemplateElement) -> Dict[str, Any]:
        """Serializa un elemento para exportación"""
        return {
            'element_type': element.element_type,
            'name': element.name,
            'position_x': element.position_x,
            'position_y': element.position_y,
            'width': element.width,
            'height': element.height,
            'rotation': element.rotation,
            'z_index': element.z_index,
            'content': element.content,
            'variables': element.variables,
            'style_config': element.style_config,
            'is_locked': element.is_locked,
            'is_visible': element.is_visible,
            'asset_ref': element.asset.id if element.asset else None,
        }
    
    def _serialize_asset(self, asset: TemplateAsset) -> Dict[str, Any]:
        """Serializa un asset para exportación"""
        # Generar nombre de archivo único
        original_name = os.path.basename(asset.file.name)
        filename = f"{asset.id}_{original_name}"
        
        return {
            'id': asset.id,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'category': asset.category,
            'filename': filename,
            'original_filename': original_name,
            'is_public': asset.is_public,
        }
    
    def _generate_readme(
        self,
        template: CertificateTemplate,
        elements: List[TemplateElement],
        assets: List[TemplateAsset]
    ) -> str:
        """Genera archivo README para la exportación"""
        return f"""
EXPORTACIÓN DE PLANTILLA DE CERTIFICADO
======================================

Plantilla: {template.name}
Exportado: {template.updated_at.strftime('%d/%m/%Y %H:%M:%S')}
Versión del Editor: {template.editor_version}

CONTENIDO DEL ARCHIVO:
- template.json: Configuración de la plantilla
- elements.json: Elementos de la plantilla ({len(elements)} elementos)
- assets.json: Información de assets ({len(assets)} assets)
- assets/: Carpeta con archivos de assets
- export_info.json: Metadatos de la exportación

DIMENSIONES DEL CANVAS:
- Ancho: {template.canvas_width}px
- Alto: {template.canvas_height}px

ELEMENTOS INCLUIDOS:
{chr(10).join([f"- {elem.name} ({elem.element_type})" for elem in elements])}

ASSETS INCLUIDOS:
{chr(10).join([f"- {asset.name} ({asset.asset_type})" for asset in assets])}

INSTRUCCIONES DE IMPORTACIÓN:
1. Usar la función de importación del editor de plantillas
2. Seleccionar este archivo ZIP
3. Confirmar la importación
4. La plantilla se creará con un nuevo ID

COMPATIBILIDAD:
- Versión de exportación: {self.export_version}
- Compatible con editor de plantillas v1.0+

Para más información, consultar la documentación del sistema.
        """.strip()
    
    def _extract_and_validate_zip(self, zip_content: bytes) -> Dict[str, Any]:
        """
        Extrae y valida el contenido de un ZIP de importación.
        
        Args:
            zip_content: Contenido del archivo ZIP
            
        Returns:
            Diccionario con datos extraídos
        """
        extracted_data = {
            'template': None,
            'elements': [],
            'assets': [],
            'asset_files': {}
        }
        
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(zip_content)
            temp_file.seek(0)
            
            with zipfile.ZipFile(temp_file, 'r') as zip_file:
                # Verificar estructura básica
                required_files = ['template.json', 'elements.json', 'assets.json']
                for required_file in required_files:
                    if required_file not in zip_file.namelist():
                        raise ValueError(f"Archivo requerido no encontrado: {required_file}")
                
                # Leer template.json
                template_content = zip_file.read('template.json').decode('utf-8')
                extracted_data['template'] = json.loads(template_content)
                
                # Leer elements.json
                elements_content = zip_file.read('elements.json').decode('utf-8')
                extracted_data['elements'] = json.loads(elements_content)
                
                # Leer assets.json
                assets_content = zip_file.read('assets.json').decode('utf-8')
                extracted_data['assets'] = json.loads(assets_content)
                
                # Leer archivos de assets
                for asset_info in extracted_data['assets']:
                    asset_filename = f"assets/{asset_info['filename']}"
                    if asset_filename in zip_file.namelist():
                        extracted_data['asset_files'][asset_info['id']] = zip_file.read(asset_filename)
                
                # Validar versión si existe export_info.json
                if 'export_info.json' in zip_file.namelist():
                    export_info_content = zip_file.read('export_info.json').decode('utf-8')
                    export_info = json.loads(export_info_content)
                    
                    # Verificar compatibilidad de versión
                    export_version = export_info.get('export_version', '1.0')
                    if not self._is_version_compatible(export_version):
                        logger.warning(f"Version compatibility issue: {export_version}")
        
        return extracted_data
    
    def _is_version_compatible(self, export_version: str) -> bool:
        """Verifica si la versión de exportación es compatible"""
        # Por ahora, aceptar todas las versiones 1.x
        try:
            major_version = int(export_version.split('.')[0])
            return major_version == 1
        except (ValueError, IndexError):
            return False
    
    def _import_assets(
        self, 
        assets_data: List[Dict[str, Any]], 
        overwrite: bool = False
    ) -> Dict[int, TemplateAsset]:
        """
        Importa assets y retorna mapeo de IDs antiguos a nuevos.
        
        Args:
            assets_data: Datos de assets a importar
            overwrite: Si sobrescribir assets existentes
            
        Returns:
            Mapeo de ID antiguo -> TemplateAsset nuevo
        """
        asset_mapping = {}
        
        for asset_data in assets_data:
            old_id = asset_data['id']
            
            # Verificar si ya existe un asset con el mismo nombre
            existing_asset = None
            if not overwrite:
                existing_asset = TemplateAsset.objects.filter(
                    name=asset_data['name'],
                    asset_type=asset_data['asset_type']
                ).first()
            
            if existing_asset and not overwrite:
                # Reutilizar asset existente
                asset_mapping[old_id] = existing_asset
                logger.info(f"Reusing existing asset: {existing_asset.name}")
            else:
                # Crear nuevo asset
                asset_file_content = self._get_asset_file_content(old_id, asset_data)
                
                if asset_file_content:
                    # Crear archivo Django
                    file_obj = ContentFile(
                        asset_file_content,
                        name=asset_data['original_filename']
                    )
                    
                    # Crear asset
                    new_asset = TemplateAsset.objects.create(
                        name=asset_data['name'],
                        asset_type=asset_data['asset_type'],
                        category=asset_data.get('category', ''),
                        file=file_obj,
                        is_public=asset_data.get('is_public', True)
                    )
                    
                    asset_mapping[old_id] = new_asset
                    logger.info(f"Created new asset: {new_asset.name}")
                else:
                    logger.warning(f"Could not import asset {asset_data['name']}: file not found")
        
        return asset_mapping
    
    def _get_asset_file_content(self, asset_id: int, asset_data: Dict[str, Any]) -> Optional[bytes]:
        """Obtiene el contenido del archivo de un asset"""
        # Este método sería llamado desde _extract_and_validate_zip
        # donde ya se han extraído los archivos
        return getattr(self, '_current_asset_files', {}).get(asset_id)
    
    def _create_template_from_data(
        self,
        template_data: Dict[str, Any],
        asset_mapping: Dict[int, TemplateAsset],
        new_name: Optional[str] = None
    ) -> CertificateTemplate:
        """
        Crea una nueva plantilla desde datos importados.
        
        Args:
            template_data: Datos de la plantilla
            asset_mapping: Mapeo de assets
            new_name: Nombre opcional para la nueva plantilla
            
        Returns:
            Nueva plantilla creada
        """
        # Determinar nombre
        name = new_name or template_data['name']
        
        # Asegurar nombre único
        base_name = name
        counter = 1
        while CertificateTemplate.objects.filter(name=name).exists():
            name = f"{base_name} (Copia {counter})"
            counter += 1
        
        # Obtener asset de fondo si existe
        background_asset = None
        background_asset_ref = template_data.get('background_asset_ref')
        if background_asset_ref and background_asset_ref in asset_mapping:
            background_asset = asset_mapping[background_asset_ref]
        
        # Crear plantilla
        template = CertificateTemplate.objects.create(
            name=name,
            canvas_width=template_data.get('canvas_width', 842),
            canvas_height=template_data.get('canvas_height', 595),
            render_config=template_data.get('render_config', {}),
            available_variables=template_data.get('available_variables', []),
            editor_version=template_data.get('editor_version', '1.0'),
            background_asset=background_asset,
            
            # Campos legacy
            html_template=template_data.get('html_template', ''),
            css_styles=template_data.get('css_styles', ''),
            field_positions=template_data.get('field_positions', {}),
            
            # No marcar como default
            is_default=False
        )
        
        return template
    
    def _create_elements_from_data(
        self,
        elements_data: List[Dict[str, Any]],
        template: CertificateTemplate,
        asset_mapping: Dict[int, TemplateAsset]
    ):
        """
        Crea elementos desde datos importados.
        
        Args:
            elements_data: Lista de datos de elementos
            template: Plantilla padre
            asset_mapping: Mapeo de assets
        """
        for element_data in elements_data:
            # Obtener asset si existe
            asset = None
            asset_ref = element_data.get('asset_ref')
            if asset_ref and asset_ref in asset_mapping:
                asset = asset_mapping[asset_ref]
            
            # Crear elemento
            TemplateElement.objects.create(
                template=template,
                element_type=element_data['element_type'],
                name=element_data['name'],
                position_x=element_data['position_x'],
                position_y=element_data['position_y'],
                width=element_data['width'],
                height=element_data['height'],
                rotation=element_data.get('rotation', 0),
                z_index=element_data.get('z_index', 0),
                content=element_data.get('content', ''),
                variables=element_data.get('variables', {}),
                style_config=element_data.get('style_config', {}),
                is_locked=element_data.get('is_locked', False),
                is_visible=element_data.get('is_visible', True),
                asset=asset
            )
    
    def validate_import_file(self, zip_content: bytes) -> Dict[str, Any]:
        """
        Valida un archivo de importación sin importarlo.
        
        Args:
            zip_content: Contenido del ZIP
            
        Returns:
            Información de validación
        """
        try:
            extracted_data = self._extract_and_validate_zip(zip_content)
            
            template_data = extracted_data['template']
            elements_data = extracted_data['elements']
            assets_data = extracted_data['assets']
            
            return {
                'is_valid': True,
                'template_name': template_data.get('name', 'Sin nombre'),
                'elements_count': len(elements_data),
                'assets_count': len(assets_data),
                'canvas_size': f"{template_data.get('canvas_width', 0)}x{template_data.get('canvas_height', 0)}",
                'editor_version': template_data.get('editor_version', 'Desconocida'),
                'elements_summary': [
                    {
                        'name': elem.get('name', 'Sin nombre'),
                        'type': elem.get('element_type', 'Desconocido')
                    }
                    for elem in elements_data[:10]  # Primeros 10
                ],
                'assets_summary': [
                    {
                        'name': asset.get('name', 'Sin nombre'),
                        'type': asset.get('asset_type', 'Desconocido')
                    }
                    for asset in assets_data[:10]  # Primeros 10
                ]
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'message': 'El archivo no es un archivo de plantilla válido'
            }


# Funciones de utilidad
def export_template_to_zip(template_id: int) -> bytes:
    """
    Función de utilidad para exportar una plantilla.
    
    Args:
        template_id: ID de la plantilla
        
    Returns:
        Bytes del ZIP generado
    """
    exporter = TemplateExportService()
    return exporter.export_template(template_id)


def import_template_from_zip(
    zip_content: bytes, 
    new_name: Optional[str] = None
) -> CertificateTemplate:
    """
    Función de utilidad para importar una plantilla.
    
    Args:
        zip_content: Contenido del ZIP
        new_name: Nombre opcional
        
    Returns:
        Plantilla importada
    """
    importer = TemplateExportService()
    return importer.import_template(zip_content, new_name)