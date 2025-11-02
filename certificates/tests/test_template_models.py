"""
Tests para los modelos del editor de plantillas avanzado.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from certificates.models import CertificateTemplate, TemplateElement, TemplateAsset
import json


class TemplateAssetModelTests(TestCase):
    """Tests para el modelo TemplateAsset"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear imagen de prueba
        self.test_image = SimpleUploadedFile(
            name='test_logo.png',
            content=b'fake image content',
            content_type='image/png'
        )
    
    def test_create_template_asset(self):
        """Verifica creación básica de asset"""
        asset = TemplateAsset.objects.create(
            name='Logo Institucional',
            asset_type='LOGO',
            file=self.test_image,
            category='Logos',
            created_by=self.user
        )
        
        self.assertEqual(asset.name, 'Logo Institucional')
        self.assertEqual(asset.asset_type, 'LOGO')
        self.assertEqual(asset.category, 'Logos')
        self.assertTrue(asset.is_public)
        self.assertEqual(asset.created_by, self.user)
    
    def test_asset_str_representation(self):
        """Verifica representación en string del asset"""
        asset = TemplateAsset.objects.create(
            name='Firma Digital',
            asset_type='SIGNATURE',
            file=self.test_image,
            created_by=self.user
        )
        
        expected = "Firma Digital (Firma)"
        self.assertEqual(str(asset), expected)
    
    def test_asset_types_choices(self):
        """Verifica que todos los tipos de asset están disponibles"""
        expected_types = ['BACKGROUND', 'LOGO', 'SIGNATURE', 'SEAL', 'ICON']
        asset_types = [choice[0] for choice in TemplateAsset.ASSET_TYPES]
        
        for expected_type in expected_types:
            self.assertIn(expected_type, asset_types)
    
    def test_asset_ordering(self):
        """Verifica que los assets se ordenan por fecha de creación descendente"""
        asset1 = TemplateAsset.objects.create(
            name='Asset 1',
            asset_type='LOGO',
            file=self.test_image,
            created_by=self.user
        )
        asset2 = TemplateAsset.objects.create(
            name='Asset 2',
            asset_type='LOGO',
            file=self.test_image,
            created_by=self.user
        )
        
        assets = list(TemplateAsset.objects.all())
        self.assertEqual(assets[0], asset2)  # Más reciente primero
        self.assertEqual(assets[1], asset1)


class CertificateTemplateExtendedTests(TestCase):
    """Tests para los campos extendidos del modelo CertificateTemplate"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_template_with_editor_fields(self):
        """Verifica creación de plantilla con campos del editor visual"""
        template = CertificateTemplate.objects.create(
            name='Plantilla Visual',
            html_template='<html></html>',
            canvas_width=1024,
            canvas_height=768,
            editor_version='1.0',
            last_edited_by=self.user
        )
        
        self.assertEqual(template.canvas_width, 1024)
        self.assertEqual(template.canvas_height, 768)
        self.assertEqual(template.editor_version, '1.0')
        self.assertEqual(template.last_edited_by, self.user)
    
    def test_template_default_canvas_dimensions(self):
        """Verifica dimensiones por defecto del canvas (A4 landscape)"""
        template = CertificateTemplate.objects.create(
            name='Plantilla Default',
            html_template='<html></html>'
        )
        
        self.assertEqual(template.canvas_width, 842)  # A4 width @ 72dpi
        self.assertEqual(template.canvas_height, 595)  # A4 height @ 72dpi
    
    def test_template_render_config_json(self):
        """Verifica almacenamiento de configuración de renderizado"""
        render_config = {
            'page': {
                'width': 842,
                'height': 595,
                'orientation': 'landscape'
            },
            'pdf': {
                'dpi': 300,
                'quality': 'high'
            }
        }
        
        template = CertificateTemplate.objects.create(
            name='Plantilla con Config',
            html_template='<html></html>',
            render_config=render_config
        )
        
        self.assertEqual(template.render_config['page']['width'], 842)
        self.assertEqual(template.render_config['pdf']['dpi'], 300)
    
    def test_template_available_variables(self):
        """Verifica almacenamiento de variables disponibles"""
        variables = [
            {
                'key': 'participant_name',
                'label': 'Nombre del Participante',
                'type': 'string'
            },
            {
                'key': 'event_date',
                'label': 'Fecha del Evento',
                'type': 'date'
            }
        ]
        
        template = CertificateTemplate.objects.create(
            name='Plantilla con Variables',
            html_template='<html></html>',
            available_variables=variables
        )
        
        self.assertEqual(len(template.available_variables), 2)
        self.assertEqual(template.available_variables[0]['key'], 'participant_name')
    
    def test_template_background_asset_relationship(self):
        """Verifica relación con asset de fondo"""
        test_image = SimpleUploadedFile(
            name='background.png',
            content=b'fake image',
            content_type='image/png'
        )
        
        asset = TemplateAsset.objects.create(
            name='Fondo Corporativo',
            asset_type='BACKGROUND',
            file=test_image,
            created_by=self.user
        )
        
        template = CertificateTemplate.objects.create(
            name='Plantilla con Fondo',
            html_template='<html></html>',
            background_asset=asset
        )
        
        self.assertEqual(template.background_asset, asset)
        self.assertIn(template, asset.templates_using_as_background.all())


class TemplateElementModelTests(TestCase):
    """Tests para el modelo TemplateElement"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.template = CertificateTemplate.objects.create(
            name='Plantilla de Prueba',
            html_template='<html></html>'
        )
    
    def test_create_text_element(self):
        """Verifica creación de elemento de texto"""
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Nombre del Participante',
            position_x=100,
            position_y=200,
            width=400,
            height=50,
            content='{{participant_name}}'
        )
        
        self.assertEqual(element.element_type, 'TEXT')
        self.assertEqual(element.position_x, 100)
        self.assertEqual(element.position_y, 200)
        self.assertEqual(element.content, '{{participant_name}}')
    
    def test_create_latex_element(self):
        """Verifica creación de elemento LaTeX"""
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='LATEX',
            name='Fórmula Matemática',
            position_x=300,
            position_y=400,
            width=200,
            height=100,
            content='$E = mc^2$'
        )
        
        self.assertEqual(element.element_type, 'LATEX')
        self.assertEqual(element.content, '$E = mc^2$')
    
    def test_element_default_values(self):
        """Verifica valores por defecto de elementos"""
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento Default',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Test'
        )
        
        self.assertEqual(element.rotation, 0)
        self.assertEqual(element.z_index, 0)
        self.assertFalse(element.is_locked)
        self.assertTrue(element.is_visible)
        self.assertEqual(element.variables, {})
        self.assertEqual(element.style_config, {})
    
    def test_element_style_config(self):
        """Verifica almacenamiento de configuración de estilo"""
        style_config = {
            'text': {
                'fontFamily': 'Arial',
                'fontSize': 24,
                'color': '#000000',
                'textAlign': 'center'
            },
            'border': {
                'width': 2,
                'color': '#FF0000',
                'style': 'solid'
            }
        }
        
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento con Estilo',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Test',
            style_config=style_config
        )
        
        self.assertEqual(element.style_config['text']['fontFamily'], 'Arial')
        self.assertEqual(element.style_config['border']['width'], 2)
    
    def test_element_variables_json(self):
        """Verifica almacenamiento de variables dinámicas"""
        variables = {
            'participant_name': {
                'type': 'string',
                'default': 'Nombre Completo'
            },
            'event_date': {
                'type': 'date',
                'format': 'DD/MM/YYYY'
            }
        }
        
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='VARIABLE',
            name='Variables Dinámicas',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='{{participant_name}} - {{event_date}}',
            variables=variables
        )
        
        self.assertIn('participant_name', element.variables)
        self.assertEqual(element.variables['event_date']['format'], 'DD/MM/YYYY')
    
    def test_element_z_index_ordering(self):
        """Verifica ordenamiento por z-index"""
        element1 = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento Fondo',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Fondo',
            z_index=0
        )
        
        element2 = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento Frente',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Frente',
            z_index=10
        )
        
        elements = list(TemplateElement.objects.all())
        self.assertEqual(elements[0], element1)  # z_index menor primero
        self.assertEqual(elements[1], element2)
    
    def test_element_asset_relationship(self):
        """Verifica relación con asset para elementos de imagen"""
        test_image = SimpleUploadedFile(
            name='logo.png',
            content=b'fake image',
            content_type='image/png'
        )
        
        asset = TemplateAsset.objects.create(
            name='Logo',
            asset_type='LOGO',
            file=test_image,
            created_by=self.user
        )
        
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='IMAGE',
            name='Logo Institucional',
            position_x=50,
            position_y=50,
            width=100,
            height=100,
            content='',
            asset=asset
        )
        
        self.assertEqual(element.asset, asset)
        self.assertIn(element, asset.elements_using.all())
    
    def test_element_str_representation(self):
        """Verifica representación en string del elemento"""
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Título Principal',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Certificado'
        )
        
        expected = f"Título Principal (Texto) - {self.template.name}"
        self.assertEqual(str(element), expected)
    
    def test_element_types_choices(self):
        """Verifica que todos los tipos de elemento están disponibles"""
        expected_types = ['TEXT', 'IMAGE', 'QR', 'LATEX', 'VARIABLE']
        element_types = [choice[0] for choice in TemplateElement.ELEMENT_TYPES]
        
        for expected_type in expected_types:
            self.assertIn(expected_type, element_types)
    
    def test_template_elements_relationship(self):
        """Verifica relación inversa de plantilla con elementos"""
        element1 = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento 1',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Test 1'
        )
        
        element2 = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento 2',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Test 2'
        )
        
        elements = self.template.elements.all()
        self.assertEqual(elements.count(), 2)
        self.assertIn(element1, elements)
        self.assertIn(element2, elements)
    
    def test_element_cascade_delete(self):
        """Verifica que elementos se eliminan al eliminar plantilla"""
        element = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Test'
        )
        
        template_id = self.template.id
        self.template.delete()
        
        # Verificar que el elemento también se eliminó
        self.assertFalse(
            TemplateElement.objects.filter(template_id=template_id).exists()
        )
