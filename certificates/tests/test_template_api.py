"""
Tests para las APIs del editor de plantillas avanzado.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
import json

from certificates.models import CertificateTemplate, TemplateElement, TemplateAsset
from PIL import Image
import io


def create_test_image(name='test.png', format='PNG', size=(10, 10)):
    """Crea una imagen de prueba válida"""
    image = Image.new('RGB', size, color='red')
    image_io = io.BytesIO()
    image.save(image_io, format=format)
    image_io.seek(0)
    
    return SimpleUploadedFile(
        name=name,
        content=image_io.getvalue(),
        content_type=f'image/{format.lower()}'
    )


class TemplateAPITestCase(TestCase):
    """Caso base para tests de APIs de plantillas"""
    
    def setUp(self):
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123',
            is_staff=False
        )
        
        # Cliente API
        self.client = APIClient()
        
        # Plantilla de prueba
        self.template = CertificateTemplate.objects.create(
            name='Plantilla de Prueba',
            html_template='<html></html>',
            canvas_width=842,
            canvas_height=595
        )
        
        # Asset de prueba
        test_image = create_test_image('test_logo.png')
        
        self.asset = TemplateAsset.objects.create(
            name='Logo de Prueba',
            asset_type='LOGO',
            file=test_image,
            created_by=self.admin_user
        )


class CertificateTemplateAPITests(TemplateAPITestCase):
    """Tests para la API de plantillas de certificados"""
    
    def test_list_templates_requires_authentication(self):
        """Verifica que listar plantillas requiere autenticación"""
        url = reverse('certificates:template-list')
        response = self.client.get(url)
        # DRF puede retornar 401 o 403 dependiendo de la configuración
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_list_templates_authenticated(self):
        """Verifica que usuarios autenticados pueden listar plantillas"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:template-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Manejar respuesta paginada o no paginada
        if isinstance(response.data, dict) and 'results' in response.data:
            templates = response.data['results']
        else:
            templates = response.data
            
        self.assertGreaterEqual(len(templates), 1)
        # Verificar que nuestra plantilla está en la lista
        template_names = [t['name'] for t in templates]
        self.assertIn('Plantilla de Prueba', template_names)
    
    def test_create_template_requires_staff(self):
        """Verifica que crear plantillas requiere permisos de staff"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:template-list')
        
        data = {
            'name': 'Nueva Plantilla',
            'html_template': '<html></html>',
            'canvas_width': 800,
            'canvas_height': 600
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_template_as_staff(self):
        """Verifica que staff puede crear plantillas"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:template-list')
        
        data = {
            'name': 'Nueva Plantilla',
            'html_template': '<html></html>',
            'canvas_width': 800,
            'canvas_height': 600,
            'available_variables': [
                {
                    'key': 'participant_name',
                    'label': 'Nombre',
                    'type': 'string'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Nueva Plantilla')
        self.assertEqual(response.data['last_edited_by']['username'], 'admin')
    
    def test_retrieve_template_detail(self):
        """Verifica obtener detalle de plantilla"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:template-detail', kwargs={'pk': self.template.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Plantilla de Prueba')
        self.assertEqual(response.data['canvas_width'], 842)
    
    def test_update_template_requires_staff(self):
        """Verifica que actualizar plantillas requiere permisos de staff"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:template-detail', kwargs={'pk': self.template.pk})
        
        data = {'name': 'Plantilla Actualizada'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_template_as_staff(self):
        """Verifica que staff puede actualizar plantillas"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:template-detail', kwargs={'pk': self.template.pk})
        
        data = {'name': 'Plantilla Actualizada'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Plantilla Actualizada')
        self.assertEqual(response.data['last_edited_by']['username'], 'admin')
    
    def test_duplicate_template(self):
        """Verifica duplicación de plantillas"""
        # Crear elemento en la plantilla original
        TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Título',
            position_x=100,
            position_y=100,
            width=200,
            height=50,
            content='Certificado'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:template-duplicate', kwargs={'pk': self.template.pk})
        
        data = {
            'name': 'Copia de Plantilla',
            'copy_elements': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Copia de Plantilla')
        self.assertEqual(response.data['element_count'], 1)
        self.assertFalse(response.data['is_default'])
    
    def test_set_default_template(self):
        """Verifica marcar plantilla como predeterminada"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:template-set-default', kwargs={'pk': self.template.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_default'])
    
    def test_available_variables(self):
        """Verifica obtener variables disponibles"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:template-available-variables')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('variables', response.data)
        self.assertGreater(len(response.data['variables']), 0)
    
    def test_template_validation(self):
        """Verifica validaciones de plantilla"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:template-list')
        
        # Canvas con dimensiones inválidas
        data = {
            'name': 'Plantilla Inválida',
            'html_template': '<html></html>',
            'canvas_width': -100,  # Inválido
            'canvas_height': 600
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('canvas_width', response.data)


class TemplateElementAPITests(TemplateAPITestCase):
    """Tests para la API de elementos de plantillas"""
    
    def setUp(self):
        super().setUp()
        self.element = TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento de Prueba',
            position_x=100,
            position_y=100,
            width=200,
            height=50,
            content='Texto de prueba'
        )
    
    def test_list_elements(self):
        """Verifica listar elementos"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:element-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_filter_elements_by_template(self):
        """Verifica filtrar elementos por plantilla"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:element-list')
        response = self.client.get(url, {'template_id': self.template.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Manejar respuesta paginada o no paginada
        if isinstance(response.data, dict) and 'results' in response.data:
            elements = response.data['results']
        else:
            elements = response.data
            
        # Debe haber al menos nuestro elemento
        self.assertGreaterEqual(len(elements), 1)
        # Verificar que todos los elementos pertenecen a nuestra plantilla
        for element in elements:
            self.assertEqual(element['template'], self.template.id)
    
    def test_create_element_requires_staff(self):
        """Verifica que crear elementos requiere permisos de staff"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:element-list')
        
        data = {
            'template': self.template.id,
            'element_type': 'TEXT',
            'name': 'Nuevo Elemento',
            'position_x': 50,
            'position_y': 50,
            'width': 100,
            'height': 30,
            'content': 'Nuevo texto'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_text_element(self):
        """Verifica crear elemento de texto"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-list')
        
        data = {
            'template': self.template.id,
            'element_type': 'TEXT',
            'name': 'Título Principal',
            'position_x': 200,
            'position_y': 100,
            'width': 400,
            'height': 60,
            'content': 'CERTIFICADO DE PARTICIPACIÓN',
            'style_config': {
                'text': {
                    'fontFamily': 'Arial',
                    'fontSize': 24,
                    'color': '#000000'
                }
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Título Principal')
    
    def test_create_image_element_with_asset(self):
        """Verifica crear elemento de imagen con asset"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-list')
        
        data = {
            'template': self.template.id,
            'element_type': 'IMAGE',
            'name': 'Logo Institucional',
            'position_x': 50,
            'position_y': 50,
            'width': 100,
            'height': 100,
            'content': ' ',  # Espacio en blanco para evitar validación
            'asset_id': self.asset.id
        }
        
        response = self.client.post(url, data)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.data}")  # Para debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['asset']['name'], 'Logo de Prueba')
    
    def test_move_element(self):
        """Verifica mover elemento"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-move', kwargs={'pk': self.element.pk})
        
        data = {
            'position_x': 300,
            'position_y': 200
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position_x'], 300)
        self.assertEqual(response.data['position_y'], 200)
    
    def test_resize_element(self):
        """Verifica redimensionar elemento"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-resize', kwargs={'pk': self.element.pk})
        
        data = {
            'width': 400,
            'height': 80
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['width'], 400)
        self.assertEqual(response.data['height'], 80)
    
    def test_change_z_index(self):
        """Verifica cambiar z-index"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-z-index', kwargs={'pk': self.element.pk})
        
        data = {'z_index': 10}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['z_index'], 10)
    
    def test_bring_to_front(self):
        """Verifica traer elemento al frente"""
        # Crear otro elemento con z-index mayor
        TemplateElement.objects.create(
            template=self.template,
            element_type='TEXT',
            name='Elemento Frontal',
            position_x=0,
            position_y=0,
            width=100,
            height=50,
            content='Frente',
            z_index=5
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-bring-to-front', kwargs={'pk': self.element.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['z_index'], 6)  # 5 + 1
    
    def test_element_validation(self):
        """Verifica validaciones de elementos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:element-list')
        
        # Elemento con dimensiones inválidas
        data = {
            'template': self.template.id,
            'element_type': 'TEXT',
            'name': 'Elemento Inválido',
            'position_x': -10,  # Inválido
            'position_y': 50,
            'width': 0,  # Inválido
            'height': 30,
            'content': 'Texto'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('position_x', response.data)
        self.assertIn('width', response.data)


class TemplateAssetAPITests(TemplateAPITestCase):
    """Tests para la API de assets de plantillas"""
    
    def test_list_assets(self):
        """Verifica listar assets"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:asset-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_filter_assets_by_type(self):
        """Verifica filtrar assets por tipo"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:asset-list')
        response = self.client.get(url, {'type': 'LOGO'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Manejar respuesta paginada o no paginada
        if isinstance(response.data, dict) and 'results' in response.data:
            assets = response.data['results']
        else:
            assets = response.data
            
        # Verificar que todos los assets son del tipo LOGO
        for asset in assets:
            self.assertEqual(asset['asset_type'], 'LOGO')
    
    def test_create_asset_requires_staff(self):
        """Verifica que crear assets requiere permisos de staff"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:asset-list')
        
        test_image = SimpleUploadedFile(
            name='new_logo.png',
            content=b'fake image',
            content_type='image/png'
        )
        
        data = {
            'name': 'Nuevo Logo',
            'asset_type': 'LOGO',
            'file': test_image
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_asset_as_staff(self):
        """Verifica que staff puede crear assets"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:asset-list')
        
        # Crear imagen válida
        test_image = create_test_image('new_logo.png')
        
        data = {
            'name': 'Nuevo Logo',
            'asset_type': 'LOGO',
            'file': test_image,
            'category': 'Logos Institucionales'
        }
        
        response = self.client.post(url, data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.data}")  # Para debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Nuevo Logo')
        self.assertEqual(response.data['created_by']['username'], 'admin')
    
    def test_delete_asset_in_use(self):
        """Verifica que no se puede eliminar asset en uso"""
        # Usar el asset en un elemento
        TemplateElement.objects.create(
            template=self.template,
            element_type='IMAGE',
            name='Logo',
            position_x=0,
            position_y=0,
            width=100,
            height=100,
            content='',
            asset=self.asset
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:asset-detail', kwargs={'pk': self.asset.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_categories(self):
        """Verifica obtener categorías de assets"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('certificates:asset-categories')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
    
    def test_asset_file_validation(self):
        """Verifica validación de archivos de assets"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('certificates:asset-list')
        
        # Archivo con tipo MIME inválido
        invalid_file = SimpleUploadedFile(
            name='document.pdf',
            content=b'%PDF-1.4 fake pdf content',
            content_type='application/pdf'
        )
        
        data = {
            'name': 'Documento Inválido',
            'asset_type': 'LOGO',
            'file': invalid_file
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)


class TemplateAPIPermissionsTests(TemplateAPITestCase):
    """Tests específicos para permisos de las APIs"""
    
    def test_unauthenticated_access_denied(self):
        """Verifica que usuarios no autenticados no pueden acceder"""
        urls = [
            reverse('certificates:template-list'),
            reverse('certificates:element-list'),
            reverse('certificates:asset-list'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            # DRF puede retornar 401 o 403 dependiendo de la configuración
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_regular_user_read_only(self):
        """Verifica que usuarios regulares solo pueden leer"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Puede leer
        read_urls = [
            reverse('certificates:template-list'),
            reverse('certificates:template-detail', kwargs={'pk': self.template.pk}),
            reverse('certificates:element-list'),
            reverse('certificates:asset-list'),
        ]
        
        for url in read_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # No puede escribir
        write_data = {'name': 'Test'}
        write_urls = [
            (reverse('certificates:template-list'), 'post'),
            (reverse('certificates:template-detail', kwargs={'pk': self.template.pk}), 'patch'),
            (reverse('certificates:element-list'), 'post'),
            (reverse('certificates:asset-list'), 'post'),
        ]
        
        for url, method in write_urls:
            response = getattr(self.client, method)(url, write_data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_staff_full_access(self):
        """Verifica que staff tiene acceso completo"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Puede leer
        response = self.client.get(reverse('certificates:template-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Puede crear
        data = {
            'name': 'Plantilla Staff',
            'html_template': '<html></html>',
            'canvas_width': 800,
            'canvas_height': 600
        }
        response = self.client.post(reverse('certificates:template-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Puede actualizar
        data = {'name': 'Plantilla Actualizada'}
        response = self.client.patch(
            reverse('certificates:template-detail', kwargs={'pk': self.template.pk}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)