"""
Vistas de API para el editor de plantillas avanzado.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.contrib.auth.models import User
from django.http import HttpResponse

from .models import CertificateTemplate, TemplateElement, TemplateAsset
from .serializers import (
    CertificateTemplateSerializer,
    CertificateTemplateListSerializer,
    CertificateTemplateDuplicateSerializer,
    TemplateElementSerializer,
    TemplateAssetSerializer,
)
from .services.latex_validator import LaTeXValidator
# Template renderer will be imported conditionally in views
TEMPLATE_RENDERER_AVAILABLE = True

# Create dummy classes if WeasyPrint is not available
class DummyTemplateRenderingService:
    def render_template_to_pdf(self, template_id, participant_data):
        raise ImportError("WeasyPrint is not available")
    
    def generate_preview_image(self, template_id, participant_data):
        raise ImportError("WeasyPrint is not available")

def get_sample_participant_data():
    return {
        'participant_name': 'Juan Pérez García',
        'participant_dni': '12345678',
        'event_name': 'Curso de Ejemplo',
        'event_date': '15/11/2024',
        'certificate_uuid': 'test-uuid',
        'attendee_type': 'Asistente'
    }
from .services.template_export import TemplateExportService


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite lectura a todos los usuarios autenticados
    pero solo permite escritura a usuarios staff.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Permitir lectura a todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Solo staff puede crear, editar o eliminar
        return request.user.is_staff


class CertificateTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de plantillas de certificados.
    
    Proporciona operaciones CRUD completas más acciones adicionales
    como duplicar plantillas y generar vistas previas.
    """
    
    queryset = CertificateTemplate.objects.all()
    permission_classes = [IsStaffOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return CertificateTemplateListSerializer
        elif self.action == 'duplicate':
            return CertificateTemplateDuplicateSerializer
        return CertificateTemplateSerializer
    
    def get_queryset(self):
        """Optimiza las consultas según la acción"""
        queryset = CertificateTemplate.objects.all()
        
        if self.action == 'list':
            # Para listado, prefetch elementos para contar
            queryset = queryset.prefetch_related('elements')
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Para detalle, incluir elementos y assets relacionados
            queryset = queryset.prefetch_related(
                'elements__asset',
                'background_asset'
            ).select_related('last_edited_by')
        
        return queryset.order_by('-is_default', '-updated_at')
    
    def perform_create(self, serializer):
        """Personaliza la creación de plantillas"""
        # Establecer valores por defecto si no se proporcionan
        validated_data = serializer.validated_data
        
        # Valores por defecto para campos requeridos
        if 'html_template' not in validated_data:
            validated_data['html_template'] = '<!-- Plantilla creada con editor visual -->'
        
        if 'css_styles' not in validated_data:
            validated_data['css_styles'] = '/* Estilos generados por editor visual */'
        
        if 'available_variables' not in validated_data:
            validated_data['available_variables'] = [
                'participant_name', 'participant_dni', 'event_name', 
                'event_date', 'attendee_type', 'certificate_uuid'
            ]
        
        if 'render_config' not in validated_data:
            validated_data['render_config'] = {
                'page': {
                    'width': validated_data.get('canvas_width', 842),
                    'height': validated_data.get('canvas_height', 595),
                    'orientation': 'landscape' if validated_data.get('canvas_width', 842) > validated_data.get('canvas_height', 595) else 'portrait'
                },
                'pdf': {'dpi': 300, 'quality': 'high'}
            }
        
        serializer.save(
            last_edited_by=self.request.user,
            editor_version='1.0'
        )
    
    def perform_update(self, serializer):
        """Personaliza la actualización de plantillas"""
        serializer.save(last_edited_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplica una plantilla existente.
        
        POST /api/templates/{id}/duplicate/
        {
            "name": "Nombre de la copia",
            "copy_elements": true
        }
        """
        template = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                # Crear copia de la plantilla
                new_template = CertificateTemplate.objects.create(
                    name=serializer.validated_data['name'],
                    html_template=template.html_template,
                    css_styles=template.css_styles,
                    background_image=template.background_image,
                    is_default=False,  # La copia nunca es default
                    field_positions=template.field_positions,
                    canvas_width=template.canvas_width,
                    canvas_height=template.canvas_height,
                    background_asset=template.background_asset,
                    render_config=template.render_config,
                    available_variables=template.available_variables,
                    editor_version=template.editor_version,
                    last_edited_by=request.user
                )
                
                # Copiar elementos si se solicita
                if serializer.validated_data.get('copy_elements', True):
                    elements_to_create = []
                    for element in template.elements.all():
                        elements_to_create.append(TemplateElement(
                            template=new_template,
                            element_type=element.element_type,
                            name=element.name,
                            position_x=element.position_x,
                            position_y=element.position_y,
                            width=element.width,
                            height=element.height,
                            rotation=element.rotation,
                            z_index=element.z_index,
                            content=element.content,
                            variables=element.variables,
                            asset=element.asset,
                            style_config=element.style_config,
                            is_locked=element.is_locked,
                            is_visible=element.is_visible
                        ))
                    
                    TemplateElement.objects.bulk_create(elements_to_create)
                
                # Serializar la nueva plantilla
                response_serializer = CertificateTemplateSerializer(
                    new_template,
                    context={'request': request}
                )
                
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Marca una plantilla como predeterminada.
        
        POST /api/templates/{id}/set_default/
        """
        template = self.get_object()
        
        with transaction.atomic():
            # Desmarcar todas las plantillas como default
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
            # Marcar esta como default
            template.is_default = True
            template.last_edited_by = request.user
            template.save()
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Genera una vista previa de la plantilla con datos de prueba.
        
        GET /api/templates/{id}/preview/
        """
        template = self.get_object()
        
        # Obtener datos de prueba
        test_data = get_sample_participant_data()
        
        # Permitir datos personalizados via query params
        for key in test_data.keys():
            if key in request.query_params:
                test_data[key] = request.query_params[key]
        
        try:
            # Import renderer conditionally
            try:
                from .services.template_renderer import TemplateRenderingService
                renderer = TemplateRenderingService()
            except ImportError:
                renderer = DummyTemplateRenderingService()
            
            # Verificar si se solicita PDF
            if request.query_params.get('format') == 'pdf':
                pdf_bytes = renderer.render_template_to_pdf(template.id, test_data)
                
                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="preview_{template.id}.pdf"'
                return response
            
            # Verificar si se solicita imagen
            elif request.query_params.get('format') == 'image':
                image_bytes = renderer.generate_preview_image(template.id, test_data)
                
                response = HttpResponse(image_bytes, content_type='image/png')
                response['Content-Disposition'] = f'inline; filename="preview_{template.id}.png"'
                return response
            
            # Por defecto, retornar información de la vista previa
            serializer = self.get_serializer(template)
            return Response({
                'template': serializer.data,
                'test_data': test_data,
                'preview_pdf_url': f'/api/templates/{template.id}/preview/?format=pdf',
                'preview_image_url': f'/api/templates/{template.id}/preview/?format=image',
                'available_formats': ['pdf', 'image'],
                'message': 'Vista previa disponible'
            })
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error generando vista previa',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def available_variables(self, request):
        """
        Retorna las variables disponibles del sistema.
        
        GET /api/templates/available_variables/
        """
        variables = [
            {
                'key': 'participant_name',
                'label': 'Nombre del Participante',
                'type': 'string',
                'example': 'Juan Pérez García'
            },
            {
                'key': 'participant_dni',
                'label': 'DNI del Participante',
                'type': 'string',
                'example': '12345678'
            },
            {
                'key': 'event_name',
                'label': 'Nombre del Evento',
                'type': 'string',
                'example': 'Curso de Python Avanzado'
            },
            {
                'key': 'event_date',
                'label': 'Fecha del Evento',
                'type': 'date',
                'format': 'DD/MM/YYYY',
                'example': '15/11/2024'
            },
            {
                'key': 'certificate_uuid',
                'label': 'UUID del Certificado',
                'type': 'string',
                'example': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            },
            {
                'key': 'attendee_type',
                'label': 'Tipo de Asistente',
                'type': 'string',
                'example': 'Asistente'
            }
        ]
        
        return Response({'variables': variables})
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        Exporta una plantilla completa a ZIP.
        
        POST /api/templates/{id}/export/
        """
        template = self.get_object()
        
        try:
            # Import exporter conditionally
            try:
                from .services.template_export import TemplateExportService
                exporter = TemplateExportService()
            except ImportError:
                return Response(
                    {
                        'error': 'Template export service not available',
                        'details': 'WeasyPrint dependencies are required for template export'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            zip_bytes = exporter.export_template(template.id)
            
            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="template_{template.id}_{template.name}.zip"'
            return response
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error exportando plantilla',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def import_template(self, request):
        """
        Importa una plantilla desde ZIP.
        
        POST /api/templates/import/
        Content-Type: multipart/form-data
        
        Form data:
        - file: Archivo ZIP
        - name: Nombre opcional para la plantilla
        - overwrite_assets: Si sobrescribir assets existentes
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Archivo requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        zip_file = request.FILES['file']
        new_name = request.data.get('name')
        overwrite_assets = request.data.get('overwrite_assets', 'false').lower() == 'true'
        
        try:
            # Leer contenido del archivo
            zip_content = zip_file.read()
            
            # Importar plantilla
            exporter = TemplateExportService()
            template = exporter.import_template(
                zip_content, 
                new_name, 
                overwrite_assets
            )
            
            # Serializar resultado
            serializer = self.get_serializer(template)
            return Response(
                {
                    'message': 'Plantilla importada exitosamente',
                    'template': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error importando plantilla',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def validate_import(self, request):
        """
        Valida un archivo de importación sin importarlo.
        
        POST /api/templates/validate_import/
        Content-Type: multipart/form-data
        
        Form data:
        - file: Archivo ZIP a validar
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Archivo requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        zip_file = request.FILES['file']
        
        try:
            # Leer contenido del archivo
            zip_content = zip_file.read()
            
            # Validar
            exporter = TemplateExportService()
            validation_result = exporter.validate_import_file(zip_content)
            
            return Response(validation_result)
            
        except Exception as e:
            return Response(
                {
                    'is_valid': False,
                    'error': str(e),
                    'message': 'Error validando archivo'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class TemplateElementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de elementos de plantillas.
    
    Proporciona operaciones CRUD para elementos individuales
    más acciones para manipular posición y orden.
    """
    
    queryset = TemplateElement.objects.all()
    serializer_class = TemplateElementSerializer
    permission_classes = [IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filtra elementos por plantilla si se especifica"""
        queryset = TemplateElement.objects.select_related('template', 'asset')
        
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        
        return queryset.order_by('z_index', 'created_at')
    
    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        """
        Mueve un elemento a una nueva posición.
        
        PATCH /api/elements/{id}/move/
        {
            "position_x": 100,
            "position_y": 200
        }
        """
        element = self.get_object()
        
        position_x = request.data.get('position_x')
        position_y = request.data.get('position_y')
        
        if position_x is not None:
            if position_x < 0:
                return Response(
                    {'error': 'position_x debe ser mayor o igual a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            element.position_x = position_x
        
        if position_y is not None:
            if position_y < 0:
                return Response(
                    {'error': 'position_y debe ser mayor o igual a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            element.position_y = position_y
        
        element.save()
        
        serializer = self.get_serializer(element)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def resize(self, request, pk=None):
        """
        Redimensiona un elemento.
        
        PATCH /api/elements/{id}/resize/
        {
            "width": 400,
            "height": 100
        }
        """
        element = self.get_object()
        
        width = request.data.get('width')
        height = request.data.get('height')
        
        if width is not None:
            if width <= 0:
                return Response(
                    {'error': 'width debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            element.width = width
        
        if height is not None:
            if height <= 0:
                return Response(
                    {'error': 'height debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            element.height = height
        
        element.save()
        
        serializer = self.get_serializer(element)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def z_index(self, request, pk=None):
        """
        Cambia el z-index (orden de capas) de un elemento.
        
        PATCH /api/elements/{id}/z_index/
        {
            "z_index": 10
        }
        """
        element = self.get_object()
        
        new_z_index = request.data.get('z_index')
        if new_z_index is None:
            return Response(
                {'error': 'z_index es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        element.z_index = new_z_index
        element.save()
        
        serializer = self.get_serializer(element)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def bring_to_front(self, request, pk=None):
        """
        Trae el elemento al frente (z-index más alto).
        
        POST /api/elements/{id}/bring_to_front/
        """
        element = self.get_object()
        
        # Encontrar el z-index más alto en la plantilla
        max_z_index = TemplateElement.objects.filter(
            template=element.template
        ).aggregate(
            max_z=models.Max('z_index')
        )['max_z'] or 0
        
        element.z_index = max_z_index + 1
        element.save()
        
        serializer = self.get_serializer(element)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_to_back(self, request, pk=None):
        """
        Envía el elemento al fondo (z-index más bajo).
        
        POST /api/elements/{id}/send_to_back/
        """
        element = self.get_object()
        
        # Encontrar el z-index más bajo en la plantilla
        min_z_index = TemplateElement.objects.filter(
            template=element.template
        ).aggregate(
            min_z=models.Min('z_index')
        )['min_z'] or 0
        
        element.z_index = min_z_index - 1
        element.save()
        
        serializer = self.get_serializer(element)
        return Response(serializer.data)


class TemplateAssetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de assets de plantillas.
    
    Proporciona operaciones CRUD para assets (imágenes, logos, etc.)
    con funcionalidades de categorización y búsqueda.
    """
    
    queryset = TemplateAsset.objects.all()
    serializer_class = TemplateAssetSerializer
    permission_classes = [IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filtra assets según parámetros de consulta"""
        queryset = TemplateAsset.objects.select_related('created_by')
        
        # Filtrar por tipo
        asset_type = self.request.query_params.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        # Filtrar por categoría
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filtrar por visibilidad
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # Búsqueda por nombre
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Personaliza la creación de assets"""
        serializer.save(created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Personaliza la eliminación para verificar uso"""
        asset = self.get_object()
        
        # Verificar si está siendo usado como fondo
        if asset.templates_using_as_background.exists():
            return Response(
                {
                    'error': 'No se puede eliminar el asset porque está siendo usado como fondo en una o más plantillas',
                    'templates': [t.name for t in asset.templates_using_as_background.all()]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si está siendo usado en elementos
        if asset.elements_using.exists():
            return Response(
                {
                    'error': 'No se puede eliminar el asset porque está siendo usado en uno o más elementos',
                    'elements': [e.name for e in asset.elements_using.all()]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Retorna las categorías disponibles de assets.
        
        GET /api/assets/categories/
        """
        categories = TemplateAsset.objects.values_list(
            'category', flat=True
        ).distinct().exclude(
            category__isnull=True
        ).exclude(
            category__exact=''
        ).order_by('category')
        
        return Response({'categories': list(categories)})


# Vista para validación de LaTeX
from rest_framework.views import APIView

class LaTeXValidationView(APIView):
    """
    Vista para validar código LaTeX.
    
    POST /api/latex/validate/
    {
        "latex_code": "$E = mc^2$"
    }
    """
    permission_classes = [IsStaffOrReadOnly]
    
    def post(self, request):
        latex_code = request.data.get('latex_code', '')
        
        if not latex_code:
            return Response(
                {'error': 'latex_code es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validator = LaTeXValidator()
        result = validator.validate_latex(latex_code)
        
        # Agregar sugerencias si hay errores
        if not result['is_valid']:
            suggestions = validator.suggest_corrections(latex_code)
            result['suggestions'] = suggestions
        
        return Response(result)


class LaTeXRenderView(APIView):
    """
    Vista para renderizar LaTeX a SVG.
    
    POST /api/latex/render/
    {
        "latex_code": "$E = mc^2$",
        "type": "inline" | "display"
    }
    """
    permission_classes = [IsStaffOrReadOnly]
    
    def post(self, request):
        latex_code = request.data.get('latex_code', '')
        render_type = request.data.get('type', 'inline')
        
        if not latex_code:
            return Response(
                {'error': 'latex_code es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar primero
        validator = LaTeXValidator()
        validation_result = validator.validate_latex(latex_code)
        
        if not validation_result['is_valid']:
            return Response(
                {
                    'error': 'Código LaTeX inválido',
                    'validation_errors': validation_result['errors']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Por ahora, retornar el código sanitizado
        # En una implementación completa, aquí se renderizaría a SVG
        sanitized_code = validation_result['sanitized_code']
        
        # Formatear según el tipo
        if render_type == 'display':
            formatted_code = f'$${sanitized_code}$$'
        else:
            formatted_code = f'${sanitized_code}$'
        
        return Response({
            'rendered_latex': formatted_code,
            'sanitized_code': sanitized_code,
            'type': render_type,
            'svg_content': None,  # TODO: Implementar renderizado real a SVG
            'message': 'Renderizado simulado - implementar MathJax server-side'
        })