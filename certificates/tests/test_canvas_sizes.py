"""
Tests para utilidades de tamaños de canvas.
"""
from django.test import TestCase
from certificates.utils.canvas_sizes import CanvasSizes, get_a4_horizontal, get_a4_vertical


class CanvasSizesTest(TestCase):
    """Tests para la clase CanvasSizes"""
    
    def test_a4_dimensions(self):
        """Test dimensiones A4 correctas"""
        # A4 Horizontal (Landscape)
        self.assertEqual(CanvasSizes.A4_HORIZONTAL, (842, 595))
        
        # A4 Vertical (Portrait)
        self.assertEqual(CanvasSizes.A4_VERTICAL, (595, 842))
    
    def test_default_size(self):
        """Test tamaño por defecto"""
        default = CanvasSizes.get_default_size()
        self.assertEqual(default, (842, 595))  # A4 Horizontal
    
    def test_size_detection(self):
        """Test detección de tamaño por dimensiones"""
        # A4 Horizontal
        detected = CanvasSizes.detect_size_from_dimensions(842, 595)
        self.assertEqual(detected, 'a4_horizontal')
        
        # A4 Vertical
        detected = CanvasSizes.detect_size_from_dimensions(595, 842)
        self.assertEqual(detected, 'a4_vertical')
        
        # Tamaño personalizado
        detected = CanvasSizes.detect_size_from_dimensions(1000, 600)
        self.assertEqual(detected, 'custom')
    
    def test_orientation_detection(self):
        """Test detección de orientación"""
        # Landscape
        self.assertTrue(CanvasSizes.is_landscape(842, 595))
        self.assertFalse(CanvasSizes.is_portrait(842, 595))
        
        # Portrait
        self.assertTrue(CanvasSizes.is_portrait(595, 842))
        self.assertFalse(CanvasSizes.is_landscape(595, 842))
        
        # Square
        self.assertTrue(CanvasSizes.is_square(800, 800))
        self.assertFalse(CanvasSizes.is_landscape(800, 800))
        self.assertFalse(CanvasSizes.is_portrait(800, 800))
    
    def test_print_conversion(self):
        """Test conversión a DPI de impresión"""
        # 72 DPI a 300 DPI
        print_size = CanvasSizes.convert_to_print_dpi(842, 595, 300)
        expected_width = int(842 * (300/72))  # 3508
        expected_height = int(595 * (300/72))  # 2479
        
        self.assertEqual(print_size, (expected_width, expected_height))
    
    def test_django_choices(self):
        """Test generación de choices para Django"""
        choices = CanvasSizes.get_choices_for_django()
        
        # Debe ser una lista de tuplas
        self.assertIsInstance(choices, list)
        self.assertTrue(len(choices) > 0)
        
        # Cada elemento debe ser una tupla (key, display)
        for choice in choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)
            key, display = choice
            self.assertIsInstance(key, str)
            self.assertIsInstance(display, str)
    
    def test_recommended_for_certificates(self):
        """Test tamaños recomendados para certificados"""
        recommended = CanvasSizes.get_recommended_for_certificates()
        
        # Debe incluir al menos A4 horizontal
        self.assertIn('a4_horizontal', recommended)
        
        # Debe ser una lista no vacía
        self.assertTrue(len(recommended) > 0)
    
    def test_size_info_completeness(self):
        """Test que toda la información de tamaños esté completa"""
        for key, info in CanvasSizes.SIZES.items():
            # Campos requeridos
            required_fields = [
                'name', 'description', 'dimensions', 
                'orientation', 'recommended_for', 'print_size_mm'
            ]
            
            for field in required_fields:
                self.assertIn(field, info, f"Campo {field} faltante en {key}")
            
            # Dimensiones deben ser tupla de 2 enteros
            dimensions = info['dimensions']
            self.assertIsInstance(dimensions, tuple)
            self.assertEqual(len(dimensions), 2)
            self.assertIsInstance(dimensions[0], int)
            self.assertIsInstance(dimensions[1], int)
            
            # Dimensiones deben ser positivas
            self.assertGreater(dimensions[0], 0)
            self.assertGreater(dimensions[1], 0)


class CanvasSizesUtilityFunctionsTest(TestCase):
    """Tests para funciones de utilidad"""
    
    def test_get_a4_horizontal(self):
        """Test función de utilidad A4 horizontal"""
        size = get_a4_horizontal()
        self.assertEqual(size, (842, 595))
    
    def test_get_a4_vertical(self):
        """Test función de utilidad A4 vertical"""
        size = get_a4_vertical()
        self.assertEqual(size, (595, 842))
    
    def test_consistency_between_functions(self):
        """Test consistencia entre diferentes funciones"""
        # A4 horizontal debe ser igual en todas las funciones
        self.assertEqual(get_a4_horizontal(), CanvasSizes.A4_HORIZONTAL)
        self.assertEqual(get_a4_horizontal(), CanvasSizes.get_size_by_key('a4_horizontal'))
        
        # A4 vertical debe ser igual en todas las funciones
        self.assertEqual(get_a4_vertical(), CanvasSizes.A4_VERTICAL)
        self.assertEqual(get_a4_vertical(), CanvasSizes.get_size_by_key('a4_vertical'))


class CanvasSizesIntegrationTest(TestCase):
    """Tests de integración con modelos Django"""
    
    def test_template_with_a4_horizontal(self):
        """Test creación de plantilla con A4 horizontal"""
        from certificates.models import CertificateTemplate
        
        width, height = get_a4_horizontal()
        template = CertificateTemplate.objects.create(
            name='Test A4 Horizontal',
            canvas_width=width,
            canvas_height=height
        )
        
        self.assertEqual(template.canvas_width, 842)
        self.assertEqual(template.canvas_height, 595)
        
        # Verificar que se detecta como landscape
        self.assertTrue(CanvasSizes.is_landscape(template.canvas_width, template.canvas_height))
    
    def test_template_with_a4_vertical(self):
        """Test creación de plantilla con A4 vertical"""
        from certificates.models import CertificateTemplate
        
        width, height = get_a4_vertical()
        template = CertificateTemplate.objects.create(
            name='Test A4 Vertical',
            canvas_width=width,
            canvas_height=height
        )
        
        self.assertEqual(template.canvas_width, 595)
        self.assertEqual(template.canvas_height, 842)
        
        # Verificar que se detecta como portrait
        self.assertTrue(CanvasSizes.is_portrait(template.canvas_width, template.canvas_height))
    
    def test_size_detection_from_template(self):
        """Test detección de tamaño desde plantilla"""
        from certificates.models import CertificateTemplate
        
        # Crear plantilla A4 horizontal
        template = CertificateTemplate.objects.create(
            name='Test Detection',
            canvas_width=842,
            canvas_height=595
        )
        
        detected_size = CanvasSizes.detect_size_from_dimensions(
            template.canvas_width, 
            template.canvas_height
        )
        
        self.assertEqual(detected_size, 'a4_horizontal')
        
        size_info = CanvasSizes.get_size_info(detected_size)
        self.assertEqual(size_info['name'], 'A4 Horizontal')
        self.assertIn('certificados', size_info['recommended_for'])