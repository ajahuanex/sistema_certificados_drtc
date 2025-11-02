"""
Serializers para las APIs del editor de plantillas avanzado.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CertificateTemplate, TemplateElement, TemplateAsset


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuarios"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class TemplateAssetSerializer(serializers.ModelSerializer):
    """Serializer para assets de plantillas"""
    
    created_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateAsset
        fields = [
            'id', 'name', 'asset_type', 'file', 'file_url', 'category',
            'is_public', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Retorna la URL completa del archivo"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def validate_file(self, value):
        """Valida el archivo subido"""
        if value:
            # Validar tamaño (máximo 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"El archivo es demasiado grande. Máximo permitido: 10MB"
                )
            
            # Validar tipo MIME
            allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"Tipo de archivo no permitido. Formatos válidos: PNG, JPG, JPEG, SVG"
                )
        
        return value


class TemplateElementSerializer(serializers.ModelSerializer):
    """Serializer para elementos de plantillas"""
    
    asset = TemplateAssetSerializer(read_only=True)
    asset_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = TemplateElement
        fields = [
            'id', 'template', 'element_type', 'name',
            'position_x', 'position_y', 'width', 'height', 'rotation', 'z_index',
            'content', 'variables', 'asset', 'asset_id', 'style_config',
            'is_locked', 'is_visible', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_position_x(self, value):
        """Valida que la posición X sea válida"""
        if value < 0:
            raise serializers.ValidationError("La posición X debe ser mayor o igual a 0")
        return value
    
    def validate_position_y(self, value):
        """Valida que la posición Y sea válida"""
        if value < 0:
            raise serializers.ValidationError("La posición Y debe ser mayor o igual a 0")
        return value
    
    def validate_width(self, value):
        """Valida que el ancho sea válido"""
        if value <= 0:
            raise serializers.ValidationError("El ancho debe ser mayor a 0")
        return value
    
    def validate_height(self, value):
        """Valida que el alto sea válido"""
        if value <= 0:
            raise serializers.ValidationError("El alto debe ser mayor a 0")
        return value
    
    def validate_rotation(self, value):
        """Valida que la rotación esté en el rango válido"""
        if not (0 <= value <= 360):
            raise serializers.ValidationError("La rotación debe estar entre 0 y 360 grados")
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Si es elemento de imagen, debe tener asset
        if data.get('element_type') == 'IMAGE' and not data.get('asset_id'):
            raise serializers.ValidationError({
                'asset_id': 'Los elementos de tipo IMAGE requieren un asset'
            })
        
        # Si es elemento LaTeX, validar sintaxis básica
        if data.get('element_type') == 'LATEX':
            content = data.get('content', '')
            if not content.strip():
                raise serializers.ValidationError({
                    'content': 'Los elementos LaTeX requieren contenido'
                })
        
        return data


class CertificateTemplateSerializer(serializers.ModelSerializer):
    """Serializer para plantillas de certificados"""
    
    elements = TemplateElementSerializer(many=True, read_only=True)
    background_asset = TemplateAssetSerializer(read_only=True)
    background_asset_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    last_edited_by = UserSerializer(read_only=True)
    element_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CertificateTemplate
        fields = [
            'id', 'name', 'html_template', 'css_styles', 'background_image',
            'is_default', 'field_positions', 'created_at', 'updated_at',
            'canvas_width', 'canvas_height', 'background_asset', 'background_asset_id',
            'render_config', 'available_variables', 'editor_version', 'last_edited_by',
            'elements', 'element_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_edited_by']
    
    def get_element_count(self, obj):
        """Retorna el número de elementos en la plantilla"""
        return obj.elements.count()
    
    def validate_canvas_width(self, value):
        """Valida el ancho del canvas"""
        if value <= 0:
            raise serializers.ValidationError("El ancho del canvas debe ser mayor a 0")
        if value > 5000:  # Límite razonable
            raise serializers.ValidationError("El ancho del canvas no puede exceder 5000px")
        return value
    
    def validate_canvas_height(self, value):
        """Valida el alto del canvas"""
        if value <= 0:
            raise serializers.ValidationError("El alto del canvas debe ser mayor a 0")
        if value > 5000:  # Límite razonable
            raise serializers.ValidationError("El alto del canvas no puede exceder 5000px")
        return value
    
    def validate_available_variables(self, value):
        """Valida la estructura de variables disponibles"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Las variables disponibles deben ser una lista")
        
        for variable in value:
            if not isinstance(variable, dict):
                raise serializers.ValidationError("Cada variable debe ser un objeto")
            
            required_fields = ['key', 'label', 'type']
            for field in required_fields:
                if field not in variable:
                    raise serializers.ValidationError(
                        f"La variable debe tener el campo '{field}'"
                    )
        
        return value
    
    def validate_render_config(self, value):
        """Valida la configuración de renderizado"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("La configuración de renderizado debe ser un objeto")
        return value


class CertificateTemplateListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de plantillas"""
    
    last_edited_by = UserSerializer(read_only=True)
    element_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CertificateTemplate
        fields = [
            'id', 'name', 'is_default', 'canvas_width', 'canvas_height',
            'editor_version', 'last_edited_by', 'element_count',
            'created_at', 'updated_at'
        ]
    
    def get_element_count(self, obj):
        """Retorna el número de elementos en la plantilla"""
        return obj.elements.count()


class CertificateTemplateDuplicateSerializer(serializers.Serializer):
    """Serializer para duplicar plantillas"""
    
    name = serializers.CharField(
        max_length=200,
        help_text="Nombre para la plantilla duplicada"
    )
    copy_elements = serializers.BooleanField(
        default=True,
        help_text="Si se deben copiar también los elementos"
    )
    
    def validate_name(self, value):
        """Valida que el nombre no esté en uso"""
        if CertificateTemplate.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Ya existe una plantilla con este nombre"
            )
        return value