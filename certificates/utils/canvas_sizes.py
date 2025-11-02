"""
Utilidades para gestión de tamaños de canvas y conversiones.
"""
from typing import Tuple, Dict, List


class CanvasSizes:
    """
    Clase para gestionar tamaños estándar de canvas para certificados.
    
    Todos los tamaños están en píxeles a 72 DPI (resolución web estándar).
    Para impresión de alta calidad, se escalan a 300 DPI automáticamente.
    """
    
    # Tamaños A4 (210 × 297 mm)
    A4_HORIZONTAL = (842, 595)  # Landscape - Ideal para certificados
    A4_VERTICAL = (595, 842)    # Portrait - Para diplomas o documentos largos
    
    # Tamaños Carta US (216 × 279 mm)
    CARTA_HORIZONTAL = (792, 612)  # US Letter Landscape
    CARTA_VERTICAL = (612, 792)    # US Letter Portrait
    
    # Tamaños personalizados comunes
    CUADRADO_GRANDE = (800, 800)   # Formato cuadrado
    PANORAMICO = (1200, 600)       # Formato panorámico
    
    # Diccionario de todos los tamaños disponibles
    SIZES = {
        'a4_horizontal': {
            'name': 'A4 Horizontal',
            'description': 'A4 Apaisado (842×595px) - Ideal para certificados',
            'dimensions': A4_HORIZONTAL,
            'orientation': 'landscape',
            'recommended_for': ['certificados', 'diplomas', 'reconocimientos'],
            'print_size_mm': (297, 210),
            'is_default': True
        },
        'a4_vertical': {
            'name': 'A4 Vertical',
            'description': 'A4 Vertical (595×842px) - Para documentos largos',
            'dimensions': A4_VERTICAL,
            'orientation': 'portrait',
            'recommended_for': ['diplomas', 'constancias', 'cartas'],
            'print_size_mm': (210, 297),
            'is_default': False
        },
        'carta_horizontal': {
            'name': 'Carta Horizontal',
            'description': 'Carta US Apaisado (792×612px)',
            'dimensions': CARTA_HORIZONTAL,
            'orientation': 'landscape',
            'recommended_for': ['certificados_us'],
            'print_size_mm': (279, 216),
            'is_default': False
        },
        'carta_vertical': {
            'name': 'Carta Vertical',
            'description': 'Carta US Vertical (612×792px)',
            'dimensions': CARTA_VERTICAL,
            'orientation': 'portrait',
            'recommended_for': ['documentos_us'],
            'print_size_mm': (216, 279),
            'is_default': False
        },
        'cuadrado': {
            'name': 'Cuadrado Grande',
            'description': 'Formato Cuadrado (800×800px)',
            'dimensions': CUADRADO_GRANDE,
            'orientation': 'square',
            'recommended_for': ['badges', 'sellos', 'logos'],
            'print_size_mm': (282, 282),
            'is_default': False
        },
        'panoramico': {
            'name': 'Panorámico',
            'description': 'Formato Panorámico (1200×600px)',
            'dimensions': PANORAMICO,
            'orientation': 'panoramic',
            'recommended_for': ['banners', 'headers'],
            'print_size_mm': (423, 212),
            'is_default': False
        }
    }
    
    @classmethod
    def get_default_size(cls) -> Tuple[int, int]:
        """Retorna el tamaño por defecto (A4 Horizontal)"""
        return cls.A4_HORIZONTAL
    
    @classmethod
    def get_size_by_key(cls, key: str) -> Tuple[int, int]:
        """
        Obtiene dimensiones por clave.
        
        Args:
            key: Clave del tamaño ('a4_horizontal', 'a4_vertical', etc.)
            
        Returns:
            Tupla (width, height) en píxeles
        """
        if key in cls.SIZES:
            return cls.SIZES[key]['dimensions']
        return cls.get_default_size()
    
    @classmethod
    def get_size_info(cls, key: str) -> Dict:
        """
        Obtiene información completa de un tamaño.
        
        Args:
            key: Clave del tamaño
            
        Returns:
            Diccionario con información completa
        """
        return cls.SIZES.get(key, cls.SIZES['a4_horizontal'])
    
    @classmethod
    def get_all_sizes(cls) -> Dict:
        """Retorna todos los tamaños disponibles"""
        return cls.SIZES
    
    @classmethod
    def get_choices_for_django(cls) -> List[Tuple]:
        """
        Retorna opciones formateadas para Django choices.
        
        Returns:
            Lista de tuplas (key, display_name)
        """
        choices = []
        for key, info in cls.SIZES.items():
            width, height = info['dimensions']
            display = f"{info['name']} ({width}×{height}px)"
            choices.append((key, display))
        return choices
    
    @classmethod
    def get_recommended_for_certificates(cls) -> List[str]:
        """Retorna tamaños recomendados para certificados"""
        recommended = []
        for key, info in cls.SIZES.items():
            if 'certificados' in info['recommended_for']:
                recommended.append(key)
        return recommended
    
    @classmethod
    def convert_to_print_dpi(cls, width: int, height: int, target_dpi: int = 300) -> Tuple[int, int]:
        """
        Convierte dimensiones de 72 DPI a DPI de impresión.
        
        Args:
            width: Ancho en píxeles a 72 DPI
            height: Alto en píxeles a 72 DPI
            target_dpi: DPI objetivo (por defecto 300)
            
        Returns:
            Tupla (width, height) en píxeles al DPI objetivo
        """
        scale_factor = target_dpi / 72
        return (int(width * scale_factor), int(height * scale_factor))
    
    @classmethod
    def get_print_dimensions(cls, key: str, dpi: int = 300) -> Tuple[int, int]:
        """
        Obtiene dimensiones para impresión en alta resolución.
        
        Args:
            key: Clave del tamaño
            dpi: DPI para impresión (por defecto 300)
            
        Returns:
            Tupla (width, height) en píxeles para impresión
        """
        width, height = cls.get_size_by_key(key)
        return cls.convert_to_print_dpi(width, height, dpi)
    
    @classmethod
    def detect_size_from_dimensions(cls, width: int, height: int) -> str:
        """
        Detecta el tipo de tamaño basado en dimensiones.
        
        Args:
            width: Ancho en píxeles
            height: Alto en píxeles
            
        Returns:
            Clave del tamaño detectado o 'custom' si no coincide
        """
        for key, info in cls.SIZES.items():
            if info['dimensions'] == (width, height):
                return key
        return 'custom'
    
    @classmethod
    def is_landscape(cls, width: int, height: int) -> bool:
        """Determina si las dimensiones son apaisadas (landscape)"""
        return width > height
    
    @classmethod
    def is_portrait(cls, width: int, height: int) -> bool:
        """Determina si las dimensiones son verticales (portrait)"""
        return height > width
    
    @classmethod
    def is_square(cls, width: int, height: int) -> bool:
        """Determina si las dimensiones son cuadradas"""
        return width == height


# Funciones de utilidad para uso directo
def get_a4_horizontal() -> Tuple[int, int]:
    """Shortcut para A4 horizontal"""
    return CanvasSizes.A4_HORIZONTAL

def get_a4_vertical() -> Tuple[int, int]:
    """Shortcut para A4 vertical"""
    return CanvasSizes.A4_VERTICAL

def get_default_certificate_size() -> Tuple[int, int]:
    """Tamaño por defecto recomendado para certificados"""
    return CanvasSizes.A4_HORIZONTAL

def get_canvas_choices():
    """Choices para formularios Django"""
    return CanvasSizes.get_choices_for_django()